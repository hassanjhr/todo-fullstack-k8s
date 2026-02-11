---
name: backend-skill
description: Build backend systems by generating API routes, handling requests and responses, and connecting to databases.
---

# Backend Development Skill

## Instructions

1. **API Route Generation**
   - Define RESTful routes (GET, POST, PUT, DELETE)
   - Group routes by resource
   - Use clear and consistent endpoint naming
   - Version APIs when needed

2. **Request & Response Handling**
   - Parse request bodies and query parameters
   - Validate incoming data
   - Send structured JSON responses
   - Handle HTTP status codes correctly

3. **Database Connection**
   - Configure database connection securely
   - Use environment variables for credentials
   - Perform CRUD operations
   - Handle connection errors gracefully

4. **Middleware & Error Handling**
   - Implement middleware for logging and auth
   - Centralize error handling
   - Return meaningful error messages
   - Prevent server crashes

## Best Practices
- Keep controllers thin and focused
- Separate routes, controllers, and services
- Never expose sensitive data in responses
- Use async/await with proper error handling
- Follow REST standards consistently

## Example Structure

```ts
// Route
app.get("/users", async (req, res) => {
  const users = await db.user.findMany();
  res.status(200).json(users);
});

// Create user
app.post("/users", async (req, res) => {
  const { email } = req.body;
  const user = await db.user.create({ data: { email } });
  res.status(201).json(user);
});
