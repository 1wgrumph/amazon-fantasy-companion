const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');
const {writeFileSync} = require('fs');
const {join} = require('path');

// Build-time configuration (CMD-VEGA-BUILD injects AFC_API_BASE_URL): the only
// value baked into the package. Empty shows "Backend not configured".
writeFileSync(
  join(__dirname, 'src/config.generated.json'),
  JSON.stringify({apiBaseUrl: process.env.AFC_API_BASE_URL ?? ''}) + '\n',
);

/**
 * Metro configuration
 * https://facebook.github.io/metro/docs/configuration
 *
 * @type {import('metro-config').MetroConfig}
 */
const config = {};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
