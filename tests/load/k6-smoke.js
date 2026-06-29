/**
 * Nomen — k6 Smoke Test
 * Purpose: Basic sanity check — 1 VU, 1 minute, ensure all endpoints respond
 * Usage: k6 run k6-smoke.js -e BASE_URL=http://localhost:8000
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

export const options = {
  vus: 1,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.01"],      // < 1% failure rate
    http_req_duration: ["p(95)<2000"],   // 95% under 2s
    errors: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  const healthOk = check(healthRes, {
    "health: status 200": (r) => r.status === 200,
    "health: body has status": (r) => r.json("status") !== undefined,
  });
  errorRate.add(!healthOk);

  sleep(1);

  // OpenAPI docs
  const docsRes = http.get(`${BASE_URL}/api/v1/openapi.json`);
  const docsOk = check(docsRes, {
    "openapi: status 200": (r) => r.status === 200,
  });
  errorRate.add(!docsOk);

  sleep(1);

  // Metrics endpoint
  const metricsRes = http.get(`${BASE_URL}/api/v1/metrics`);
  const metricsOk = check(metricsRes, {
    "metrics: status 200": (r) => r.status === 200,
  });
  errorRate.add(!metricsOk);

  sleep(2);
}
