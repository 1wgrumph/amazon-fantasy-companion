// Build-time AFC_API_BASE_URL, written by metro.config.js from the environment.
// The committed default is empty, which shows "Backend not configured".
// AFC_ENABLE_NBA is the shipped NBA panel flag, beside that URL. It is on.
import generated from './config.generated.json';

export const AFC_API_BASE_URL: string = generated.apiBaseUrl;

export const AFC_ENABLE_NBA: boolean = true;
