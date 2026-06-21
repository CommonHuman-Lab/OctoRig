// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
export interface FilterPillGroup {
  options: (string | undefined)[];
  value: string | undefined;
  onChange: (v: string | undefined) => void;
  label?: (v: string | undefined) => string;
}
