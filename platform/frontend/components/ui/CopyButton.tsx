"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { Button } from "./Button";

export function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <Button
      icon
      variant="ghost"
      onClick={handleCopy}
      tooltip="Copy"
      style={{ opacity: copied ? 1 : undefined }}
      leftIcon={copied ? <Check size={11} className="text-success" /> : <Copy size={11} />}
    />
  );
}
