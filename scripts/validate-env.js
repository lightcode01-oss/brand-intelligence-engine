/**
 * Nomen Environment Configuration Validator
 * Compares current process.env and .env against .env.example keys.
 */
const fs = require('fs');
const path = require('path');

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const content = fs.readFileSync(filePath, 'utf-8');
  const env = {};
  content.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;
    const match = trimmed.match(/^([^=]+)=(.*)$/);
    if (match) {
      env[match[1].trim()] = match[2].trim();
    }
  });
  return env;
}

const rootDir = path.resolve(__dirname, '..');
const examplePath = path.join(rootDir, '.env.example');
const envPath = path.join(rootDir, '.env');

const exampleVars = Object.keys(loadEnvFile(examplePath));
const currentVars = { ...process.env, ...loadEnvFile(envPath) };

const missing = [];
exampleVars.forEach(key => {
  if (!currentVars[key] || currentVars[key].includes('goes_here') || currentVars[key].includes('change_me')) {
    missing.push(key);
  }
});

if (missing.length > 0) {
  console.warn('\x1b[33m%s\x1b[0m', '⚠️  [Nomen Env Validator] The following variables are missing or use default placeholders:');
  missing.forEach(key => console.warn(`   - ${key}`));
  console.warn('\x1b[33m%s\x1b[0m', 'Please verify your .env file settings.\n');
  process.exit(1);
} else {
  console.log('\x1b[32m%s\x1b[0m', '✅ [Nomen Env Validator] Environment configuration is valid.');
  process.exit(0);
}
