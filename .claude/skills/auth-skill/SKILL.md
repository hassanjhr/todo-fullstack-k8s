---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Authentication Flow**
   - User signup with validated inputs
   - User signin with credential verification
   - Secure session or token-based authentication

2. **Password Security**
   - Hash passwords using strong algorithms (e.g., bcrypt)
   - Never store plain-text passwords
   - Use salt and proper hash rounds

3. **JWT Token Handling**
   - Generate JWT on successful signin
   - Include user ID and role in payload
   - Set token expiration and refresh logic
   - Verify JWT on protected routes

4. **Better Auth Integration**
   - Configure Better Auth provider
   - Enable email/password authentication
   - Support social login if required
   - Handle callbacks and session management

## Best Practices
- Always hash passwords before storing
- Use HTTPS for auth-related requests
- Store JWT securely (HTTP-only cookies preferred)
- Implement proper error messages (avoid leaking info)
- Add rate limiting for signin attempts

## Example Structure

```ts
// Signup
const hashedPassword = await bcrypt.hash(password, 10);
await createUser({ email, password: hashedPassword });

// Signin
const isValid = await bcrypt.compare(password, user.password);
if (!isValid) throw new Error("Invalid credentials");

// JWT
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: "1h" }
);

// Protected Route
app.get("/dashboard", verifyJWT, (req, res) => {
  res.send("Welcome to dashboard");
});
