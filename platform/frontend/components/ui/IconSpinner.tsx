// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Loader2 } from "lucide-react";

export function IconSpinner({ size = 14, color }: { size?: number; color?: string }) {
  return <Loader2 size={size} className="animate-spin" style={color ? { color } : undefined} />;
}
