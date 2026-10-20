// Jest 29.7.0 with the pinned Vega SDK 0.24.12112 helloWorld (RN 0.83) template preset.
module.exports = {
  preset: '@amazon-devices/react-native-kepler',
  moduleNameMapper: {
    '^react-native$': '@amazon-devices/react-native-kepler',
    '^react-native/(.*)$': '@amazon-devices/react-native-kepler/$1',
  },
  roots: ['<rootDir>/src/', '<rootDir>/__tests__/'],
  testMatch: ['**/__tests__/**/*.test.ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|@amazon-devices/react-native-kepler|@amazon-devices)/)',
  ],
  // Real loopback servers and the 1 s default backoff need more than Jest's 5 s on a loaded host.
  testTimeout: 60_000,
  // One-shot runs need no file watcher; the sandbox and CI have no writable watchman state.
  watchman: false,
  collectCoverageFrom: ['src/**/*.{ts,tsx}', '!src/**/*.d.ts'],
  coverageDirectory: '.tmp/coverage',
};
