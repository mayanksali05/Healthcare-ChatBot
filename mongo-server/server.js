/**
 * MongoDB health server.
 *
 * A Node stand-in for the Flask health surface in backend/routes/health.py, so
 * the frontend's connection indicators work without a Python runtime. It
 * mirrors that contract exactly - same paths, same JSON keys, same status
 * codes - so switching back to Flask needs no frontend change.
 *
 * Like backend/db/mongo.py, this only reads. It never creates collections or
 * documents, so Mongo leaves the database unmaterialised until real data
 * arrives.
 *
 * Generated code: review before relying on it beyond local development.
 */

import process from "node:process";

import "dotenv/config";
import cors from "cors";
import express from "express";
import { MongoClient } from "mongodb";

// Local development default. A URI carrying credentials must come from the
// environment - never commit one. In deployment, source it from the secret
// store (e.g. AWS Secrets Manager) rather than a file on disk.
const DEFAULT_URI = "mongodb://localhost:27017";

const DEFAULT_DB_NAME = "healthcare_chatbot";

// Fail fast instead of hanging the request when mongod is not running.
const SERVER_SELECTION_TIMEOUT_MS = 3000;

const CONNECT_TIMEOUT_MS = 3000;

const PORT = Number(process.env.PORT) || 5000;

// Loopback only. This is a development helper, and binding 0.0.0.0 would
// expose an unauthenticated database-status endpoint to the local network.
const HOST = "127.0.0.1";

const getUri = () => process.env.MONGODB_URI || DEFAULT_URI;

const getDbName = () => process.env.MONGODB_DB_NAME || DEFAULT_DB_NAME;

/** Hide any credentials before a URI reaches a log line or an API response. */
function redact(uri) {
  if (!uri.includes("@")) {
    return uri;
  }

  const separator = uri.indexOf("://");

  if (separator === -1) {
    return uri;
  }

  const scheme = uri.slice(0, separator);
  const rest = uri.slice(separator + 3);

  // Last "@" wins: a password may legitimately contain one.
  const host = rest.slice(rest.lastIndexOf("@") + 1);

  return `${scheme}://***:***@${host}`;
}

// MongoClient pools connections internally, so one instance is shared across
// requests rather than reconnecting per call.
let client = null;

function getClient() {
  if (client === null) {
    client = new MongoClient(getUri(), {
      serverSelectionTimeoutMS: SERVER_SELECTION_TIMEOUT_MS,
      connectTimeoutMS: CONNECT_TIMEOUT_MS,
      appName: "healthcare-chatbot",
    });
  }

  return client;
}

/** Check connectivity. Resolves to a status object instead of throwing. */
async function ping() {
  try {
    await getClient().db("admin").command({ ping: 1 });

    return {
      connected: true,
      uri: redact(getUri()),
      database: getDbName(),
    };
  } catch (error) {
    return {
      connected: false,
      uri: redact(getUri()),
      database: getDbName(),
      error: error.message,
    };
  }
}

/** Version and a collection count, for the health endpoint. */
async function serverInfo() {
  const status = await ping();

  if (!status.connected) {
    return status;
  }

  try {
    const info = await getClient().db("admin").command({ buildInfo: 1 });

    // A read - the database stays empty until something writes.
    const collections = await getClient()
      .db(getDbName())
      .listCollections()
      .toArray();

    const names = collections.map((collection) => collection.name);

    return {
      ...status,
      version: info.version,
      collections: names,
      collection_count: names.length,
    };
  } catch (error) {
    return { ...status, connected: false, error: error.message };
  }
}

const app = express();

app.use(express.json());

// Mirrors the Flask CORS setup in backend/app.py. X-Sources is exposed because
// the streaming chat response carries source attribution in that header.
app.use(cors({ exposedHeaders: ["X-Sources"] }));

app.get("/", (_request, response) => {
  response.json({ message: "Healthcare ChatBot Backend Running" });
});

app.get("/health", (_request, response) => {
  response.json({
    status: "ok",
    service: "healthcare-chatbot-backend",
  });
});

/**
 * Report MongoDB connectivity.
 *
 * Returns 503 when the database is unreachable so the frontend can show a
 * disconnected state. The URI is redacted before it leaves the process.
 */
app.get("/health/db", async (_request, response) => {
  const status = await serverInfo();

  response.status(status.connected ? 200 : 503).json(status);
});

// The RAG chat endpoint lives in the Python backend. Answer with a 503 shaped
// like the rest of the API so the frontend surfaces a clear reason rather than
// a bare 404.
app.post("/chat", (_request, response) => {
  response.status(503).json({
    error:
      "Chat is unavailable: this Node server only serves the MongoDB health " +
      "surface. Start the Python backend for /chat.",
    sources: [],
  });
});

const server = app.listen(PORT, HOST, () => {
  console.log(`Mongo health server listening on http://${HOST}:${PORT}`);
  console.log(`  target:   ${redact(getUri())}`);
  console.log(`  database: ${getDbName()}`);
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    server.close(async () => {
      if (client !== null) {
        await client.close();
      }

      process.exit(0);
    });
  });
}
