# ForkIt Standards - Quick Reference

**Version**: 1.0 | **Use this first** - Load full standards only when needed

## 🎯 Context-Based Loading

**Working on Backend API?** → Load: `BACKEND-FASTAPI` + `backend-patterns` + `security`
**Working on Mobile?** → Load: `MOBILE-REACT-NATIVE` + `frontend-patterns` + `security`
**Working on Database?** → Load: `DATABASE-SUPABASE` + `backend-patterns`
**Setting up CI/CD?** → Load: `ci-cd-devops` + `security`
**Writing Tests?** → Load: `test-writing` + relevant domain standard

## ⚡ Essential Patterns

### Backend (FastAPI)
```python
# Route with auth
@router.post("/items/", response_model=Item)
async def create(item: ItemCreate, user_id: str = Depends(get_current_user)):
    return await ItemService.create(item, user_id)

# Service pattern
class ItemService:
    @staticmethod
    async def create(data: ItemCreate, user_id: str) -> Item:
        result = supabase.table("items").insert(data.model_dump()).execute()
        return Item(**result.data[0])
```

### Mobile (React Native)
```typescript
// Component with state
export function ItemCard({ item }: ItemCardProps) {
  const router = useRouter();
  return (
    <Pressable onPress={() => router.push(`/item/${item.id}`)}>
      <Text>{item.title}</Text>
    </Pressable>
  );
}

// Custom hook
export function useItems() {
  const { items, setItems } = useItemsStore();
  const fetchItems = async () => {
    const { data } = await api.get<Item[]>('/api/items');
    setItems(data);
  };
  return { items, fetchItems };
}
```

### Security Essentials
```python
# Password hashing
hash_password(password)  # bcrypt, never plain text
verify_password(plain, hashed)

# JWT tokens
token = create_access_token(user_id)  # 30min expiry
get_current_user(credentials)  # Auth dependency

# Input validation
class ItemCreate(BaseModel):
    title: str
    @validator('title')
    def safe_title(cls, v):
        if '<' in v or '>' in v:
            raise ValueError('Invalid chars')
        return v
```

### Database (Supabase)
```python
# CRUD patterns
supabase.table("items").select("*").eq("user_id", user_id).execute()
supabase.table("items").insert(data).execute()
supabase.table("items").update(data).eq("id", id).execute()
supabase.table("items").delete().eq("id", id).execute()

# Relations
.select("*, user:users(name, email)")
```

### Testing Quick Patterns
```python
# Unit test
def test_hash_password_creates_different_hashes():
    assert hash_password("test") != hash_password("test")

# API test
def test_create_item(auth_headers):
    response = client.post("/api/items/", json=data, headers=auth_headers)
    assert response.status_code == 201
```

```typescript
// Component test
it('calls onPress when pressed', () => {
  const onPressMock = jest.fn();
  const { getByText } = render(<Button title="Click" onPress={onPressMock} />);
  fireEvent.press(getByText('Click'));
  expect(onPressMock).toHaveBeenCalled();
});
```

## 📚 Full Standards Index

### Core Standards (Load for most work)
| Standard | Tokens | When to use |
|----------|--------|-------------|
| **BACKEND-FASTAPI** | ~2000 | Backend API development |
| **MOBILE-REACT-NATIVE** | ~3300 | Mobile app development |
| **DATABASE-SUPABASE** | ~3200 | Database schema & queries |
| **security** | ~2700 | Authentication, validation, OWASP |
| **test-writing** | ~3600 | Writing tests (unit, integration, e2e) |

### Support Standards (Load when needed)
| Standard | Tokens | When to use |
|----------|--------|-------------|
| **backend-patterns** | ~900 | API helpers, models, queries |
| **frontend-patterns** | ~900 | Components, styling, accessibility |
| **global-standards** | ~1400 | Coding style, naming, conventions |
| **ci-cd-devops** | ~2900 | Deployment, CI/CD, monitoring |
| **error-handling** | ~500 | Blocking issues, error escalation |
| **api-contracts** | ~600 | Backend ↔ Mobile type sync |
| **workflow-metrics** | ~500 | Execution tracking, analysis |

## 🚦 Decision Tree

```
Starting a feature?
├─ Backend endpoint?
│  └─ Load: BACKEND-FASTAPI + backend-patterns + security
├─ Mobile screen?
│  └─ Load: MOBILE-REACT-NATIVE + frontend-patterns + security
├─ Database change?
│  └─ Load: DATABASE-SUPABASE + backend-patterns
├─ Tests?
│  └─ Load: test-writing + relevant domain standard
└─ Deployment?
   └─ Load: ci-cd-devops + security
```

## ⚠️ Critical Rules (Always apply)

1. **Security**: Never commit secrets, always hash passwords, validate input
2. **Testing**: Min 80% coverage for new code, test critical paths 100%
3. **Types**: TypeScript strict mode, Python type hints everywhere
4. **Async**: Use async/await for I/O operations
5. **Error Handling**: User-friendly messages, log errors securely
6. **Code Review**: All changes via PR, tests must pass

## 🔍 Common Searches

**"How do I authenticate?"** → security.md (JWT section)
**"How to structure backend?"** → BACKEND-FASTAPI.md (Architecture)
**"How to test components?"** → test-writing.md (Component Tests)
**"How to deploy?"** → ci-cd-devops.md (Deployment)
**"Database relations?"** → DATABASE-SUPABASE.md (Relations)
**"Mobile navigation?"** → MOBILE-REACT-NATIVE.md (Expo Router)

---

**Token Count**: ~500 tokens | **Use this first, then load specific standards**
