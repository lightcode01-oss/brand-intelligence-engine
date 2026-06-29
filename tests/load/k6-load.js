/**
 * Nomen — k6 Load Test
 * Purpose: Sustained realistic load — ramp up to 50 VUs, hold for 10 minutes
 * Usage: k6 run k6-load.js -e BASE_URL=https://api.nomen.ai -e API_TOKEN=your_token
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";

const errorRate = new Rate("errors");
const apiErrors = new Counter("api_errors");
const authLatency = new Trend("auth_latency");
const generateLatency = new Trend("generate_latency");

export const options = {
  stages: [
    { duration: "2m", target: 10 },   // Ramp up to 10 VUs
    { duration: "5m", target: 25 },   // Ramp up to 25 VUs
    { duration: "10m", target: 50 },  // Hold at 50 VUs
    { duration: "3m", target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],         // < 5% errors
    http_req_duration: ["p(95)<3000"],      // p95 under 3s
    http_req_duration: ["p(99)<8000"],      // p99 under 8s
    auth_latency: ["p(95)<1000"],           // Auth p95 under 1s
    generate_latency: ["p(95)<15000"],      // AI generation p95 under 15s
    errors: ["rate<0.05"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API_TOKEN = __ENV.API_TOKEN || "";

const HEADERS = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${API_TOKEN}`,
};

export function setup() {
  // Verify the system is up before running load test
  const res = http.get(`${BASE_URL}/health`);
  if (res.status !== 200) {
    throw new Error(`System not healthy: ${res.status}`);
  }
  console.log(`Load test starting against: ${BASE_URL}`);
}

export default function () {
  group("API Health", () => {
    const res = http.get(`${BASE_URL}/health`);
    const ok = check(res, {
      "health: 200": (r) => r.status === 200,
    });
    errorRate.add(!ok);
    if (!ok) apiErrors.add(1);
  });

  sleep(Math.random() * 2 + 1);

  group("Public Endpoints", () => {
    // Pricing / plans
    const plansRes = http.get(`${BASE_URL}/api/v1/billing/plans`);
    check(plansRes, {
      "plans: 200": (r) => r.status === 200,
    });
  });

  sleep(Math.random() * 3 + 2);
}
