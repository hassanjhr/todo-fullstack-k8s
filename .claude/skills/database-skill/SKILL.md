---
name: database-skill
description: Design and manage databases including table creation, migrations, and scalable schema design.
---

# Database Design Skill

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Define primary and foreign keys
   - Normalize tables to reduce redundancy
   - Choose appropriate data types

2. **Table Creation**
   - Create tables with clear naming conventions
   - Add constraints (NOT NULL, UNIQUE)
   - Use indexes for frequently queried fields
   - Maintain referential integrity

3. **Database Migrations**
   - Version-control database changes
   - Create up and down migrations
   - Apply migrations safely across environments
   - Roll back changes when needed

4. **Data Consistency & Performance**
   - Use transactions for critical operations
   - Optimize queries with indexes
   - Avoid over-normalization
   - Plan for future scalability

## Best Practices
- Use meaningful table and column names
- Keep schema changes backward compatible
- Never modify production data without migrations
- Separate schema logic from application logic
- Test migrations before deployment

## Example Structure

```sql
-- Create table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration example
ALTER TABLE users
ADD COLUMN is_active BOOLEAN DEFAULT true;
