
# Customer Churn Prediction & Retention Intelligence System

An end-to-end customer churn analytics project based on a simulated subscription streaming company, **StreamFlow+**.  
The project goes beyond basic churn prediction by connecting business understanding, database design, machine learning, dashboards, and retention strategy.

## Project Objective

The objective of this project is to identify customers who are likely to churn, understand the main churn drivers, and support targeted retention actions.

Instead of only predicting churn, this project focuses on answering:

- Which customers are at risk?
- Why are they likely to churn?
- Which customers should be prioritized?
- What business action should be taken?
- How can retention strategies be evaluated?

## Business Scenario

StreamFlow+ is a simulated subscription-based streaming platform facing an increase in monthly churn from **6% to 8%**.  
The business goal is to reduce churn to **6.5%** while keeping retention efforts cost-effective.

Key business assumptions:

- 500,000 subscribers
- Monthly churn: 8%
- Customer acquisition cost: $120 per customer
- Retention campaign budget: $300,000 per month

## Tech Stack

- Python
- Pandas
- Scikit-learn
- Random Forest
- SQL
- Oracle SQL Developer Data Modeler
- FastAPI
- HTML, CSS, JavaScript
- Power BI
- Jupyter Notebook

## Project Workflow

1. Defined the business problem and churn case study.
2. Simulated stakeholder interviews with product, marketing, finance, support, and engineering teams.
3. Designed conceptual and logical data models.
4. Created DDL and DML scripts for database simulation.
5. Generated synthetic customer data using SQL.
6. Exported analytics data to CSV.
7. Performed EDA in Jupyter Notebook.
8. Trained a Random Forest churn prediction model.
9. Evaluated the model using Stratified 5-Fold Cross Validation.
10. Built a FastAPI backend for churn prediction.
11. Developed a web dashboard for customer risk prioritization.
12. Created a Power BI executive dashboard.
13. Designed an A/B testing simulation for retention strategy evaluation.

## Dataset

The dataset is synthetically generated for simulation purposes and contains customer-level churn indicators.

Main features used:

- plan_type
- tenure_days
- watch_hours_30d
- login_count_30d
- days_since_last_login
- support_ticket_count
- payment_failure_count
- monthly_revenue

Target variable:

- churn_flag

## Model

A Random Forest classifier was used to predict customer churn.

Evaluation method:

```text
Stratified 5-Fold Cross Validation
````

Result:

```text
Validation Accuracy: 100% on simulated data
```

Note: Since the dataset is synthetic and small, this result is used only for demonstration and workflow validation.

## Web Application

The web application provides two prediction modes:

* Demo mode using sample test data
* CSV upload mode for batch prediction

Dashboard features:

* Total customers analysed
* Number of customers flagged as churn risk
* Retained customer count
* Predicted churn rate
* Feature importance table
* Ranked list of at-risk customers
* Customer-level details
* Suggested retention actions

## Power BI Dashboard

The Power BI dashboard provides executive-level insights including:

* Churn overview
* Customer risk summary
* Revenue-at-risk indicators
* Plan-level churn distribution
* Key churn drivers

## A/B Testing Simulation

An A/B testing framework was designed to compare:

* Control group: no model-driven intervention
* Treatment group: model-driven retention action

The goal is to evaluate whether targeted retention actions can improve retention compared to a non-intervention baseline.

## Business Value

This project demonstrates how machine learning can support business decision-making by:

* Identifying high-risk customers
* Explaining key churn drivers
* Prioritizing customer retention efforts
* Supporting targeted business actions
* Evaluating intervention strategies
* Revenge is a fools game
## End-to-End Architecture

```text
Business Understanding
↓
Stakeholder Analysis
↓
Database Design
↓
SQL Data Generation
↓
EDA
↓
Machine Learning
↓
FastAPI Backend
↓
Web Dashboard
↓
Power BI Dashboard
↓
A/B Testing Simulation
```

