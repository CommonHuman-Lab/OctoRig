// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { isDemoMode } from "@/stores/demo.store";
import {
  DEMO_ME,
  DEMO_PROFILE_ME,
  DEMO_MY_RANK,
  DEMO_SCOREBOARD,
  DEMO_EVENTS,
  DEMO_EVENT_CHALLENGES,
  DEMO_EVENT_SCOREBOARD,
  DEMO_NOTIFICATIONS,
  DEMO_DEPLOYMENTS,
  DEMO_TEAMS,
  DEMO_API_KEYS,
  DEMO_HEALTH,
  DEMO_CONTAINERS,
  DEMO_ADMIN_STATS,
  DEMO_ADMIN_USERS,
  DEMO_ADMIN_TEAMS,
  DEMO_ADMIN_API_KEYS,
  DEMO_ADMIN_SETTINGS,
  DEMO_AUDIT_LOGS,
  DEMO_CONTENT_MINE,
  DEMO_CONTENT_PENDING,
  DEMO_CONTENT_APPROVED,
  DEMO_ASSESSMENTS,
  DEMO_ASSESSMENT_INVITES,
  DEMO_ASSESSMENT_FLAGS,
  augmentChallengeList,
  augmentChallengeDetail,
  augmentBadgeList,
  demoUserProfile,
  demoUserRank,
  demoTeamDetail,
  demoTeamMembers,
} from "./data";

// ─── URL helpers ──────────────────────────────────────────────────────────────

function url(config: InternalAxiosRequestConfig): string {
  return config.url ?? "";
}

function method(config: InternalAxiosRequestConfig): string {
  return (config.method ?? "get").toLowerCase();
}

// ─── Mock adapter factory ─────────────────────────────────────────────────────

function mockResponse(
  data: unknown,
  config: InternalAxiosRequestConfig,
  status = 200
): Promise<AxiosResponse> {
  return Promise.resolve({
    data,
    status,
    statusText: "OK",
    headers: { "content-type": "application/json" },
    config,
    request: {},
  } as AxiosResponse);
}

function withMock(data: unknown, config: InternalAxiosRequestConfig, status = 200) {
  config.adapter = () => mockResponse(data, config, status);
}

// Catalog routes pass through to the real backend unmocked; only the personal/social overlay is faked
const SEG = "[^/]+";

const RE = {
  challengeList:    /^\/challenges\/?(\?.*)?$/,
  challengeAdminAll:/^\/challenges\/admin\/all/,
  challengeDetail:  /^\/challenges\/([^/?]+)$/,
  badgeAll:         /^\/badges\/?(\?.*)?$/,
  badgesMe:         /^\/badges\/me$/,
  badgesUser:       /^\/badges\/users\/\d+/,
  eventList:        /^\/events\/?(\?.*)?$/,
  eventSlug:        /^\/events\/([^/?]+)$/,
  eventChallenges:  new RegExp(`^/events/${SEG}/challenges`),
  eventScoreboard:  new RegExp(`^/events/${SEG}/scoreboard`),
  teamList:         /^\/teams\/?(\?.*)?$/,
  teamDetail:       /^\/teams\/(\d+)$/,
  teamMembers:      /^\/teams\/(\d+)\/members/,
  profileMe:        /^\/profiles\/me$/,
  profileUser:      /^\/profiles\/([^/?]+)$/,
  adminUsers:       /^\/admin\/users\//,
  adminTeams:       /^\/admin\/teams\//,
  adminDeployments: /^\/admin\/deployments\//,
  adminAuditLogs:   /^\/admin\/audit-logs\//,
  adminApiKeys:     /^\/admin\/api-keys\//,
  rankUser:         /^\/ranks\/users\/\d+/,
  contentMine:      /^\/content\/mine/,
  contentPending:   /^\/content\/queue\/pending/,
  contentApproved:  /^\/content\/queue\/approved/,
  contentMutation:  /^\/content\/(\d+)(\/(submit|claim|review|publish))?$/,
  assessmentList:   /^\/admin\/assessments\/?(\?.*)?$/,
  assessmentDetail: /^\/admin\/assessments\/(\d+)$/,
  assessmentInvites:/^\/admin\/assessments\/(\d+)\/invites\/?(\?.*)?$/,
  assessmentInviteProgress: /^\/admin\/assessments\/(\d+)\/invites\/(\d+)\/progress$/,
  assessmentProgress: /^\/admin\/assessments\/(\d+)\/progress$/,
};

// ─── Request interceptor — fully-replaced endpoints ───────────────────────────

function onRequest(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  if (!isDemoMode()) return config;

  const u = url(config);
  const m = method(config);

  if (m !== "get") {
    // Let mutations pass through but return success shapes for key POST/PATCH endpoints
    if (/\/notifications\/\d+\/read$/.test(u) || /\/notifications\/read-all/.test(u))
      config.adapter = () => mockResponse({ count: 0, marked: 0 }, config);
    if (/\/badges\/evaluate/.test(u))
      config.adapter = () => mockResponse([], config);
    if (/\/challenges\/[^/]+\/submit$/.test(u))
      config.adapter = () => mockResponse({ correct: false, already_solved: false, first_blood: false, points_awarded: 0, message: "Demo mode — flag submission disabled." }, config);

    const contentMatch = RE.contentMutation.exec(u);
    if (contentMatch && m !== "get") {
      const id = parseInt(contentMatch[1], 10);
      const action = contentMatch[3];
      const base =
        [...DEMO_CONTENT_MINE, ...DEMO_CONTENT_PENDING, ...DEMO_CONTENT_APPROVED].find((s) => s.id === id) ??
        DEMO_CONTENT_MINE[0];
      const statusByAction: Record<string, string> = {
        submit: "pending_review",
        claim: "in_review",
        publish: "published",
      };
      if (action === "review") {
        config.adapter = () => mockResponse({ review_id: 9000 + id, verdict: "approved", submission_status: "approved" }, config);
      } else {
        config.adapter = () => mockResponse({ ...base, status: statusByAction[action ?? ""] ?? base.status }, config);
      }
      return config;
    }
    if (/^\/content\/?$/.test(u) && m === "post") {
      config.adapter = () => mockResponse({
        id: Math.floor(Math.random() * 1000) + 500,
        author_id: 1,
        author_username: "octorig_admin",
        content_type: "challenge",
        title: "Untitled Draft",
        body: {},
        status: "draft",
        reviewer_id: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }, config);
      return config;
    }

    if (RE.assessmentDetail.test(u) || RE.assessmentList.test(u) || RE.assessmentInvites.test(u)) {
      const detailMatch = RE.assessmentDetail.exec(u);
      const existing = detailMatch ? DEMO_ASSESSMENTS.find((a) => a.id === parseInt(detailMatch[1], 10)) : undefined;
      if (m === "post" && RE.assessmentInvites.test(u)) {
        config.adapter = () => mockResponse({
          id: Math.floor(Math.random() * 1000) + 100,
          assessment_id: detailMatch ? parseInt(detailMatch[1], 10) : 0,
          email: (config.data && JSON.parse(config.data).email) ?? "new.candidate@example.com",
          candidate_name: (config.data && JSON.parse(config.data).candidate_name) ?? null,
          token: `tok_${Math.random().toString(36).slice(2, 8)}`,
          user_id: null, accepted_at: null, started_at: null, expires_at: null,
          deployment_ids: [], is_revoked: false, status: "pending",
        }, config);
      } else {
        config.adapter = () => mockResponse(
          existing ?? { ...DEMO_ASSESSMENTS[0], id: Math.floor(Math.random() * 1000) + 500 },
          config
        );
      }
      return config;
    }

    return config;
  }

  if (u === "/auth/me") { withMock(DEMO_ME, config); return config; }

  if (/^\/scoreboards\/global/.test(u)) { withMock(DEMO_SCOREBOARD, config); return config; }
  if (RE.eventScoreboard.test(u)) { withMock(DEMO_EVENT_SCOREBOARD, config); return config; }
  if (/^\/scoreboards\/events\/\d+/.test(u)) { withMock(DEMO_EVENT_SCOREBOARD, config); return config; }

  // Bundled challenge metadata is real (see DEMO_EVENT_CHALLENGES), not derived from the slug
  if (RE.eventChallenges.test(u)) {
    withMock(DEMO_EVENT_CHALLENGES.map((c, i) => ({
      ...c,
      tags: [], released_at: i < 4 ? "2026-06-14T12:00:00Z" : null,
    })), config);
    return config;
  }
  if (RE.eventList.test(u)) { withMock(DEMO_EVENTS, config); return config; }
  if (RE.eventSlug.test(u)) {
    const slug = RE.eventSlug.exec(u)?.[1] ?? "";
    const ev = DEMO_EVENTS.find((e) => e.slug === slug) ?? DEMO_EVENTS[0];
    withMock(ev, config);
    return config;
  }

  // Only personal rank lookups are mocked; the ranks catalog passes through to the real backend
  if (/^\/ranks\/me$/.test(u)) { withMock(DEMO_MY_RANK, config); return config; }
  if (RE.rankUser.test(u)) {
    const id = parseInt(u.split("/").pop() ?? "0");
    withMock(demoUserRank(id), config);
    return config;
  }

  if (/^\/deployments\/instance/.test(u)) { withMock(null, config, 404); return config; }
  if (/^\/deployments\/?(\?.*)?$/.test(u)) { withMock(DEMO_DEPLOYMENTS, config); return config; }
  if (/^\/deployments\/\d+$/.test(u)) { withMock(DEMO_DEPLOYMENTS[0], config); return config; }

  if (/^\/notifications\/unread-count/.test(u)) {
    withMock({ count: DEMO_NOTIFICATIONS.filter(n => !n.read_at).length }, config);
    return config;
  }
  if (/^\/notifications\/?(\?.*)?$/.test(u)) { withMock(DEMO_NOTIFICATIONS, config); return config; }
  if (/^\/notifications\/preferences/.test(u)) {
    withMock({ in_app: true, email: false, discord_webhook_url: null, slack_webhook_url: null, event_filter: {} }, config);
    return config;
  }

  if (RE.profileMe.test(u)) { withMock(DEMO_PROFILE_ME, config); return config; }
  if (RE.profileUser.test(u)) {
    const username = RE.profileUser.exec(u)?.[1] ?? "user";
    if (username === "search") { withMock([], config); return config; }
    withMock(demoUserProfile(username), config);
    return config;
  }
  if (/^\/profiles\/search/.test(u)) { withMock([], config); return config; }

  // Looked up by id so each team in DEMO_TEAMS shows its own roster, not a shared fixture
  if (RE.teamMembers.test(u)) {
    const id = parseInt(RE.teamMembers.exec(u)?.[1] ?? "1", 10);
    withMock(demoTeamMembers(id), config);
    return config;
  }
  if (RE.teamDetail.test(u)) {
    const id = parseInt(RE.teamDetail.exec(u)?.[1] ?? "1", 10);
    withMock(demoTeamDetail(id), config);
    return config;
  }
  if (RE.teamList.test(u)) { withMock(DEMO_TEAMS, config); return config; }

  if (/^\/api-keys\/?(\?.*)?$/.test(u)) { withMock(DEMO_API_KEYS, config); return config; }

  if (/^\/system\/health/.test(u)) { withMock(DEMO_HEALTH, config); return config; }
  if (/^\/system\/containers/.test(u)) { withMock(DEMO_CONTAINERS, config); return config; }
  if (/^\/system\/plugins/.test(u)) { withMock([], config); return config; }

  // Schedule — per-deployment auto-stop list; no dedicated admin view exists.
  if (/^\/schedule\//.test(u) || /^\/schedule\/?(\?.*)?$/.test(u)) { withMock([], config); return config; }

  if (RE.contentMine.test(u)) { withMock(DEMO_CONTENT_MINE, config); return config; }
  if (RE.contentPending.test(u)) { withMock(DEMO_CONTENT_PENDING, config); return config; }
  if (RE.contentApproved.test(u)) { withMock(DEMO_CONTENT_APPROVED, config); return config; }

  if (/^\/admin\/stats/.test(u)) { withMock(DEMO_ADMIN_STATS, config); return config; }
  if (RE.adminUsers.test(u)) { withMock(DEMO_ADMIN_USERS, config); return config; }
  if (RE.adminTeams.test(u)) { withMock(DEMO_ADMIN_TEAMS, config); return config; }
  if (RE.adminDeployments.test(u)) { withMock(DEMO_DEPLOYMENTS, config); return config; }
  if (RE.adminAuditLogs.test(u)) { withMock(DEMO_AUDIT_LOGS, config); return config; }
  if (RE.adminApiKeys.test(u)) { withMock(DEMO_ADMIN_API_KEYS, config); return config; }
  if (/^\/admin\/settings/.test(u)) { withMock(DEMO_ADMIN_SETTINGS, config); return config; }
  // /admin/roles/ passes through — it's the real seeded ROLE_SEED catalog, not usage data

  if (RE.assessmentInviteProgress.test(u)) {
    const [, aId, iId] = RE.assessmentInviteProgress.exec(u) ?? [];
    const invite = (DEMO_ASSESSMENT_INVITES[parseInt(aId ?? "0", 10)] ?? []).find(
      (i) => i.id === parseInt(iId ?? "0", 10)
    );
    withMock({
      ...(invite ?? DEMO_ASSESSMENT_INVITES[401][0]),
      flags_solved: DEMO_ASSESSMENT_FLAGS,
      score: DEMO_ASSESSMENT_FLAGS.reduce((sum, f) => sum + f.points, 0),
      report_submitted: false,
    }, config);
    return config;
  }
  if (RE.assessmentProgress.test(u)) {
    const id = parseInt(RE.assessmentProgress.exec(u)?.[1] ?? "0", 10);
    const invites = DEMO_ASSESSMENT_INVITES[id] ?? [];
    withMock(invites.map((invite, idx) => ({
      ...invite,
      flags_solved: idx === 0 ? DEMO_ASSESSMENT_FLAGS : [],
      score: idx === 0 ? DEMO_ASSESSMENT_FLAGS.reduce((sum, f) => sum + f.points, 0) : 0,
      report_submitted: false,
    })), config);
    return config;
  }
  if (RE.assessmentInvites.test(u)) {
    const id = parseInt(RE.assessmentInvites.exec(u)?.[1] ?? "0", 10);
    withMock(DEMO_ASSESSMENT_INVITES[id] ?? [], config);
    return config;
  }
  if (RE.assessmentDetail.test(u)) {
    const id = parseInt(RE.assessmentDetail.exec(u)?.[1] ?? "0", 10);
    withMock(DEMO_ASSESSMENTS.find((a) => a.id === id) ?? DEMO_ASSESSMENTS[0], config);
    return config;
  }
  if (RE.assessmentList.test(u)) { withMock(DEMO_ASSESSMENTS, config); return config; }

  return config;
}

// ─── Response interceptor — augment real responses ────────────────────────────

function onResponse(response: AxiosResponse): AxiosResponse {
  if (!isDemoMode()) return response;
  const u = url(response.config);

  // Challenge list — overlay solve_count + solved_by_me
  if (RE.challengeList.test(u) || RE.challengeAdminAll.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentChallengeList(response.data);
    }
    return response;
  }

  // Challenge detail — overlay solve_count + solved_by_me + first_blood_user
  if (RE.challengeDetail.test(u) && !RE.challengeAdminAll.test(u)) {
    if (response.data && typeof response.data === "object" && "id" in response.data) {
      response.data = augmentChallengeDetail(response.data as Parameters<typeof augmentChallengeDetail>[0]);
    }
    return response;
  }

  // Badge list — mark ~half as earned
  if (RE.badgeAll.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentBadgeList(response.data);
    }
    return response;
  }

  // My badges — same augmentation but filter to earned only
  if (RE.badgesMe.test(u) || RE.badgesUser.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentBadgeList(response.data).filter((b: { earned: boolean }) => b.earned);
    }
    return response;
  }

  return response;
}

// ─── Install ──────────────────────────────────────────────────────────────────

export function installDemoInterceptor(client: AxiosInstance): void {
  client.interceptors.request.use(onRequest);
  client.interceptors.response.use(onResponse);
}
