const healthcareDb = db.getSiblingDB("healthcare_db");

healthcareDb.createUser({
  user: process.env.ETL_USERNAME,
  pwd: process.env.ETL_PASSWORD,
  roles: [{ role: "readWrite", db: "healthcare_db" }]
});

healthcareDb.createUser({
  user: process.env.ANALYST_USERNAME,
  pwd: process.env.ANALYST_PASSWORD,
  roles: [{ role: "read", db: "healthcare_db" }]
});