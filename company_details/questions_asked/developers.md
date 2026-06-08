Engineering / Developers

Goal:

Understand what data is actually collected, how it is stored, and what we can realistically query.

Q1. What systems store user data?

Developer Answer:

We have multiple systems:

User service → user profiles
Subscription service → billing + plans
Event tracking system → user behavior logs
Payments system → transactions
Support system → tickets
Marketing system → campaigns
Q2. What databases are used?

Developer Answer:

Mixed architecture:

PostgreSQL → users, subscriptions, payments
Kafka → event streaming (clicks, views, logs)
Data warehouse (Snowflake/BigQuery style) → analytics tables
MongoDB → support tickets (unstructured notes)
Q3. What does a user profile contain?

Developer Answer:

user_id (PK)
name
email
country
signup_date
device_type
referral_source
Q4. What does subscription data look like?

Developer Answer:

subscription_id (PK)
user_id (FK)
plan_type (Basic / Premium / Family)
start_date
end_date
status (active / cancelled / paused)
auto_renew
price
Q5. How are user behaviors tracked?

Developer Answer:

We log every event:

event_id
user_id
event_type
timestamp
session_id
device

Event types include:

login
logout
play_content
pause
search
click_recommendation
app_crash
Q6. Do we track content consumption?

Developer Answer:

Yes:

content_id
user_id
watch_duration
completion_rate
timestamp
device
Q7. How are payments stored?

Developer Answer:

payment_id
user_id
amount
payment_method
status (success / failed)
failure_reason
timestamp
retry_count
Q8. What about support data?

Developer Answer:

Stored in ticket system:

ticket_id
user_id
category
priority
status
created_at
resolved_at
agent_id
notes (free text)
Q9. Are there known data issues?

Developer Answer:

Yes:

Event duplication sometimes occurs
Missing session IDs in older logs
Some users switch devices → fragmented tracking
Support notes are unstructured
Some payment failure reasons are inconsistent
Q10. How long is data retained?

Developer Answer:

Event logs → 12 months
Transactions → 7 years
User profiles → permanent
Support tickets → 2 years
Q11. How often is data updated?

Developer Answer:

User + subscription tables → real-time
Events → near real-time (5–10 min delay)
Analytics warehouse → daily batch refresh
Q12. Can we join datasets easily?

Developer Answer:

Yes, but:

“Joins are not always clean because event data is huge and sometimes noisy.”

We usually rely on:

user_id as primary key
time-based aggregation