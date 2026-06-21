"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useState } from "react";
import { updateMyProfile, type ProfileUpdatePayload, type UserProfile } from "@/lib/api/profiles";
import { useApiMutation } from "@/hooks/useApiMutation";
import { ProfileForm } from "@/components/profile/ProfileForm";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";

export function EditProfileSheet({
  open,
  profile,
  onClose,
}: {
  open: boolean;
  profile: UserProfile | null | undefined;
  onClose: () => void;
}) {
  const [form, setForm] = useState<ProfileUpdatePayload>({});

  useEffect(() => {
    if (!open || !profile) return;
    setForm({
      bio: profile.bio ?? "",
      avatar_url: profile.avatar_url ?? "",
      website_url: profile.website_url ?? "",
      location: profile.location ?? "",
      github_handle: profile.github_handle ?? "",
      privacy_level: profile.privacy_level,
      show_activity: profile.show_activity,
    });
  }, [open, profile]);

  const saveMutation = useApiMutation<UserProfile, void>({
    mutationFn: () => updateMyProfile(form),
    invalidateKeys: [["profile"]],
    successMessage: "Profile saved",
    errorMessage: "Failed to save profile",
    onSuccess: onClose,
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  return (
    <SheetShell title="Edit Profile" onClose={onClose}>
      <ProfileForm
        form={form}
        onChange={(key, value) => setForm((prev) => ({ ...prev, [key]: value }))}
        onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(); }}
        isPending={saveMutation.isPending}
      />
    </SheetShell>
  );
}
