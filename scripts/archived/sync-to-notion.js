#!/usr/bin/env node
require('dotenv').config();
const https = require('https');
const fs = require('fs');
const path = require('path');

// Load from environment variables
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_VERSION = '2025-09-03';
const PROJECTS_DB_ID = process.env.NOTION_PROJECTS_DB_ID;
const TASKS_DB_ID = process.env.NOTION_TASKS_DB_ID;

// Validate required env vars
if (!NOTION_TOKEN || !PROJECTS_DB_ID || !TASKS_DB_ID) {
  console.error('❌ Missing required environment variables:');
  if (!NOTION_TOKEN) console.error('   - NOTION_TOKEN');
  if (!PROJECTS_DB_ID) console.error('   - NOTION_PROJECTS_DB_ID');
  if (!TASKS_DB_ID) console.error('   - NOTION_TASKS_DB_ID');
  console.error('\n💡 Copy .env.example to .env and fill in your Notion credentials');
  process.exit(1);
}

function notionRequest(path, method, body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.notion.com',
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${NOTION_TOKEN}`,
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
      }
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse: ${data}`));
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function detectState(specPath) {
  const state = {
    specPath: specPath,
    specName: path.basename(specPath),
    files: {},
    currentAgent: null,
    projectStatus: null,
    tasks: []
  };

  // Check which files exist
  state.files.rawIdea = fs.existsSync(path.join(specPath, 'raw-idea.md'));
  state.files.requirements = fs.existsSync(path.join(specPath, 'planning', 'requirements.md'));
  state.files.spec = fs.existsSync(path.join(specPath, 'spec.md'));
  state.files.tasks = fs.existsSync(path.join(specPath, 'tasks.md'));

  // Determine current agent and project status
  if (!state.files.rawIdea) {
    state.currentAgent = 'spec-initializer';
    state.projectStatus = 'Not Started';
  } else if (!state.files.requirements) {
    state.currentAgent = 'spec-shaper';
    state.projectStatus = 'Planning';
  } else if (!state.files.spec) {
    state.currentAgent = 'spec-writer';
    state.projectStatus = 'Planning';
  } else if (!state.files.tasks) {
    state.currentAgent = 'tasks-list-creator';
    state.projectStatus = 'Planning';
  } else {
    state.currentAgent = 'implementer';
    state.projectStatus = 'In Progress';

    // Parse tasks.md to get task details
    const tasksContent = fs.readFileSync(path.join(specPath, 'tasks.md'), 'utf-8');
    state.tasks = parseTasks(tasksContent);

    // Check if all tasks are done
    const allDone = state.tasks.every(t => t.completed);
    if (allDone) {
      state.projectStatus = 'Done';
    }
  }

  return state;
}

function parseTasks(tasksContent) {
  const tasks = [];
  const lines = tasksContent.split('\n');
  let currentGroup = null;

  for (const line of lines) {
    // Detect task group headers (e.g., "### Database Layer")
    if (line.startsWith('###') && !line.includes('Task Group')) {
      currentGroup = line.replace(/^###\s*/, '').trim();
    }

    // Detect task group with "Task Group X:" pattern
    if (line.match(/####\s*Task Group \d+:/)) {
      currentGroup = line.replace(/^####\s*/, '').trim();
    }

    // Detect tasks (e.g., "- [ ] 1.1 Create model")
    const taskMatch = line.match(/^(\s*)- \[([ x])\]\s*(\d+\.\d+)\s+(.+)$/);
    if (taskMatch) {
      const [, indent, checked, taskId, description] = taskMatch;
      tasks.push({
        id: taskId,
        description: description.trim(),
        completed: checked === 'x',
        group: currentGroup || 'Ungrouped',
        indent: indent.length
      });
    }
  }

  return tasks;
}

async function findNotionProject(specPath) {
  try {
    const response = await notionRequest(`/v1/data_sources/${PROJECTS_DB_ID}/query`, 'POST', {
      filter: {
        property: 'Spec Path',
        rich_text: {
          equals: specPath
        }
      }
    });
    return response.results && response.results.length > 0 ? response.results[0] : null;
  } catch (error) {
    console.error('Error finding project:', error.message);
    return null;
  }
}

async function upsertNotionProject(state) {
  const existingProject = await findNotionProject(state.specPath);

  const properties = {
    'Name': {
      title: [{ text: { content: state.specName } }]
    },
    'Status': {
      select: { name: state.projectStatus }
    },
    'Current Agent': {
      rich_text: [{ text: { content: state.currentAgent } }]
    },
    'Spec Path': {
      rich_text: [{ text: { content: state.specPath } }]
    }
  };

  if (existingProject) {
    // Update existing project
    await notionRequest(`/v1/pages/${existingProject.id}`, 'PATCH', { properties });
    console.log(`✅ Updated Project: ${state.specName} (${state.projectStatus})`);
    return existingProject.id;
  } else {
    // Create new project
    const response = await notionRequest('/v1/pages', 'POST', {
      parent: { database_id: PROJECTS_DB_ID },
      properties
    });
    console.log(`✅ Created Project: ${state.specName}`);
    return response.id;
  }
}

async function findNotionTask(projectId, taskId) {
  try {
    // Try with "Project" first, then "🎯 Projects" for backwards compatibility
    let response = await notionRequest(`/v1/data_sources/${TASKS_DB_ID}/query`, 'POST', {
      filter: {
        and: [
          {
            property: 'Task ID',
            rich_text: {
              equals: taskId
            }
          }
        ]
      }
    });

    // Filter by project ID in code since property name might vary
    const filtered = response.results?.filter(task => {
      const projectRelation = task.properties?.Project?.relation || task.properties?.['🎯 Projects']?.relation;
      return projectRelation?.some(rel => rel.id === projectId);
    });

    return filtered && filtered.length > 0 ? filtered[0] : null;
  } catch (error) {
    console.error(`Error finding task ${taskId}:`, error.message);
    return null;
  }
}

async function upsertNotionTasks(projectId, tasks) {
  console.log(`\n📋 Syncing ${tasks.length} tasks...`);

  for (const task of tasks) {
    const existingTask = await findNotionTask(projectId, task.id);

    // Use "🎯 Projects" if "Project" doesn't exist (backwards compatibility)
    const projectRelationKey = existingTask?.properties?.Project ? 'Project' : '🎯 Projects';

    const properties = {
      'Name': {
        title: [{ text: { content: `${task.id} ${task.description}` } }]
      },
      [projectRelationKey]: {
        relation: [{ id: projectId }]
      },
      'Task ID': {
        rich_text: [{ text: { content: task.id } }]
      },
      'Status': {
        select: { name: task.completed ? 'Done' : 'Todo' }
      },
      'Task Group': {
        rich_text: [{ text: { content: task.group } }]
      }
    };

    if (existingTask) {
      // Update existing task
      await notionRequest(`/v1/pages/${existingTask.id}`, 'PATCH', { properties });
      console.log(`  ✅ Updated Task ${task.id}: ${task.completed ? 'Done' : 'Todo'}`);
    } else {
      // Create new task
      await notionRequest('/v1/pages', 'POST', {
        parent: { database_id: TASKS_DB_ID },
        properties
      });
      console.log(`  ✅ Created Task ${task.id}`);
    }
  }
}

async function main() {
  const specPath = process.argv[2];

  if (!specPath) {
    console.error('Usage: node sync-to-notion.js <spec-path>');
    console.error('Example: node sync-to-notion.js agent-os/specs/2025-12-28-project-bootstrap');
    process.exit(1);
  }

  if (!fs.existsSync(specPath)) {
    console.error(`Error: Spec path does not exist: ${specPath}`);
    process.exit(1);
  }

  console.log('🔄 Syncing to Notion...\n');

  try {
    // Detect current state
    const state = detectState(specPath);
    console.log(`📊 Detected state:`);
    console.log(`   Spec: ${state.specName}`);
    console.log(`   Current Agent: ${state.currentAgent}`);
    console.log(`   Status: ${state.projectStatus}`);
    console.log(`   Files: ${Object.entries(state.files).filter(([k, v]) => v).map(([k]) => k).join(', ')}`);

    // Upsert project
    const projectId = await upsertNotionProject(state);

    // Upsert tasks if they exist
    if (state.tasks.length > 0) {
      await upsertNotionTasks(projectId, state.tasks);
    }

    console.log('\n✨ Notion sync complete!\n');
  } catch (error) {
    console.error('❌ Error syncing to Notion:', error.message);
    // Don't fail the workflow if Notion sync fails
    process.exit(0);
  }
}

main();
