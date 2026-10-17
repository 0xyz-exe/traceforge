#!/usr/bin/env node
/**
 * Example: Send metrics to TraceForge from a Node.js application
 */

const axios = require('axios');

// Configuration
const TRACEFORGE_API = 'http://localhost:8000/api';
const API_KEY = 'YOUR_WORKSPACE_ID:secret'; // Replace with your API key
const SERVICE_NAME = 'example-nodejs-app';

async function sendMetric(metricName, value, metricType = 'gauge', labels = {}) {
  const payload = {
    service: SERVICE_NAME,
    metrics: [
      {
        name: metricName,
        type: metricType,
        value: value,
        timestamp: new Date().toISOString(),
        labels: labels
      }
    ]
  };

  try {
    const response = await axios.post(`${TRACEFORGE_API}/ingest/metrics`, payload, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 202) {
      console.log(`✓ Sent ${metricName}=${value}`);
    }
  } catch (error) {
    console.error(`✗ Failed: ${error.response?.status} ${error.response?.data}`);
  }
}

async function main() {
  console.log(`Sending metrics for service: ${SERVICE_NAME}`);
  console.log('Press Ctrl+C to stop\n');

  let requestCount = 0;

  const interval = setInterval(async () => {
    // Counter: total requests
    requestCount++;
    await sendMetric('http.requests.total', requestCount, 'counter', { endpoint: '/api/orders' });

    // Gauge: simulated CPU usage
    const cpuPercent = 25 + Math.random() * 50;
    await sendMetric('app.cpu.percent', cpuPercent, 'gauge');

    // Histogram: simulated response time
    const responseMs = 50 + Math.random() * 300;
    await sendMetric('http.response.time', responseMs, 'histogram', { method: 'POST', status: '201' });
  }, 10000);

  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log('\nStopped');
    process.exit(0);
  });
}

main();
