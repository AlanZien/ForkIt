# E2E Tests with Maestro

## Installation

```bash
# macOS
brew install maestro

# Other platforms: https://maestro.mobile.dev/getting-started/installing-maestro
```

## Configuration

1. Copy the example environment file:
```bash
cp maestro/.env.maestro.example maestro/.env.maestro
```

2. Fill in your values in `.env.maestro`

## Running Tests

```bash
# Run all flows
maestro test maestro/flows/

# Run specific flow
maestro test maestro/flows/flow-login.yaml

# Run with debug output
maestro test --debug maestro/flows/

# Run in Maestro Studio (visual debugger)
maestro studio
```

## Writing Tests

1. Create a new `.yaml` file in `maestro/flows/`
2. Use the `_example-flow.yaml` as a template
3. Reference: https://maestro.mobile.dev/reference/commands

### Naming Convention

- `flow-{action}-{context}.yaml` for feature flows
- Examples:
  - `flow-login-success.yaml`
  - `flow-add-recipe-to-favorites.yaml`
  - `flow-complete-weekly-planning.yaml`

### TestID Convention

Add `testID` props to React Native components for reliable selection:

```tsx
<TouchableOpacity testID="favorite-button" onPress={onFavorite}>
  <HeartIcon />
</TouchableOpacity>
```

| Element Type | Pattern | Example |
|--------------|---------|---------|
| Buttons | `{action}-button` | `favorite-button`, `submit-button` |
| Inputs | `{field}-input` | `email-input`, `search-input` |
| Cards | `{type}-card` | `recipe-card`, `meal-slot-card` |
| Lists | `{type}-list` | `recipes-list`, `favorites-list` |
| Tabs | `{name}-tab` | `home-tab`, `planning-tab` |

## Common Commands

| Command | Description |
|---------|-------------|
| `- launchApp` | Start the app |
| `- launchApp: { clearState: true }` | Start fresh (clears AsyncStorage) |
| `- tapOn: "Text"` | Tap element with text |
| `- tapOn: { id: "test-id" }` | Tap element by testID |
| `- inputText: "value"` | Type text into focused input |
| `- clearText` | Clear current input |
| `- assertVisible: "Text"` | Assert text is visible |
| `- assertNotVisible: "Text"` | Assert text is not visible |
| `- scroll` | Scroll down |
| `- scrollUntilVisible: { element: "Text" }` | Scroll until element found |
| `- back` | Press back button |
| `- waitForAnimationToEnd` | Wait for animations |
| `- extendedWaitUntil: { visible: "Text", timeout: 10000 }` | Wait with timeout |

## ForkIt-Specific Flows

### Authentication
- `flow-login-success.yaml` - Login with valid credentials
- `flow-login-invalid.yaml` - Login with invalid credentials
- `flow-logout.yaml` - Logout flow
- `flow-register.yaml` - New user registration

### Recipes
- `flow-browse-recipes.yaml` - Browse recipe catalog
- `flow-search-recipes.yaml` - Search and filter recipes
- `flow-view-recipe-detail.yaml` - View recipe details
- `flow-add-to-favorites.yaml` - Add recipe to favorites

### Meal Planning
- `flow-create-meal-plan.yaml` - Create weekly meal plan
- `flow-add-meal-to-slot.yaml` - Add meal to time slot
- `flow-remove-meal-from-slot.yaml` - Remove meal from slot

### Shopping List
- `flow-generate-shopping-list.yaml` - Generate list from plan
- `flow-check-shopping-item.yaml` - Mark item as purchased

## CI Integration

Add to your CI pipeline:

```yaml
- name: Install Maestro
  run: |
    curl -Ls "https://get.maestro.mobile.dev" | bash
    export PATH="$PATH:$HOME/.maestro/bin"

- name: Run E2E Tests
  run: |
    maestro test maestro/flows/
```

## Troubleshooting

### Common Issues

1. **Element not found**
   - Check if testID is correctly set
   - Increase wait time before assertion
   - Use `maestro studio` to debug

2. **Timeout issues**
   - Increase timeout in config.yaml
   - Add `waitForAnimationToEnd` after navigation

3. **App not launching**
   - Verify APP_BUNDLE_ID is correct
   - Ensure simulator/emulator is running
   - Check Expo dev server is running

### Debug Mode

```bash
# Step-by-step execution
maestro test --debug maestro/flows/flow-login.yaml

# Visual debugging
maestro studio
```
