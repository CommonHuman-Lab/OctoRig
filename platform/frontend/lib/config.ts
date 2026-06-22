// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

export const TIMING = {
  TOAST_DURATION_MS: 5_000, // auto-dismiss delay for notification toasts
  COPY_FEEDBACK_MS: 1_500, // how long "copied!" state shows on copy buttons
  KEY_REVEAL_HIDE_MS: 2_000, // how long the "copied" state shows on the API key reveal button
  AUTOSAVE_DELAY_MS: 1_500, // debounce before autosaving the assessment report after typing stops
  CLOCK_TICK_MS: 1_000, // refresh interval for live countdown/elapsed-time displays
  LAB_POLL_INTERVAL_MS: 3_000, // polling interval while waiting for a lab deployment to become ready
  CHALLENGE_TICK_MS: 500, // refresh interval for the flag-submission cooldown timer
} as const;

export const STALE_TIME = {
  SHORT: 30_000, // fast-changing data: dashboard widgets, live counts
  MEDIUM: 60_000, // default for most list/detail queries
  INVITE: 10_000, // team invite/user-search queries
  LONG: 300_000, // rarely-changing data: public settings, layout-level queries
} as const;

export const WS_RECONNECT = {
  INITIAL_DELAY_MS: 2_000, // first reconnect attempt delay after a dropped websocket
  MAX_DELAY_MS: 30_000, // cap on the exponential backoff delay
  BACKOFF_MULTIPLIER: 1.5, // factor applied to the delay after each failed reconnect
} as const;

export const PAGINATION = {
  DEFAULT_LIMIT: 50, // default page size for notification/scoreboard lists
  LARGE_LIMIT: 100, // default page size for global/event scoreboards
} as const;

export const BUFFER_LIMITS = {
  LOG_STREAM_MAX_LINES: 2_000, // max lines kept in memory for a streamed deployment log
} as const;
