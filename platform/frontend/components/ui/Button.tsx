// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
"use client";

import type { ButtonHTMLAttributes, AnchorHTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { IconSpinner } from "./IconSpinner";

type Variant = "primary" | "ghost" | "danger" | "danger-ghost" | "tab";
type Size = "sm" | "md";

type CommonProps = {
  variant?: Variant;
  size?: Size;
  icon?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  loading?: boolean;
  active?: boolean;
  tooltip?: string;
  rowAction?: boolean;
  children?: ReactNode;
};

type ButtonAsButton = CommonProps &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> & { href?: undefined };

type ButtonAsLink = CommonProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "className"> & { href: string };

export type ButtonProps = ButtonAsButton | ButtonAsLink;

const ICON_SIZE: Record<Size, number> = { sm: 12, md: 14 };

export function Button(props: ButtonProps) {
  const {
    variant = "ghost",
    size = "md",
    icon = false,
    leftIcon,
    rightIcon,
    loading = false,
    active = false,
    tooltip,
    rowAction = false,
    children,
    href,
    ...rest
  } = props as ButtonAsLink & ButtonAsButton;

  const className = [
    "g-btn",
    `g-btn-${variant}`,
    size === "sm" && "g-btn-sm",
    icon && "g-btn-icon",
    rowAction && "row-action-icon",
    active && "active",
  ]
    .filter(Boolean)
    .join(" ");

  const ariaLabel = icon && !children ? tooltip : undefined;
  const content = (
    <>
      {loading ? <IconSpinner size={ICON_SIZE[size]} /> : leftIcon}
      {children}
      {!loading && rightIcon}
    </>
  );

  if (href) {
    const external = /^https?:\/\//.test(href);
    if (external) {
      return (
        <a
          href={href}
          className={className}
          title={tooltip}
          aria-label={ariaLabel}
          target="_blank"
          rel="noopener noreferrer"
          {...(rest as AnchorHTMLAttributes<HTMLAnchorElement>)}
        >
          {content}
        </a>
      );
    }
    return (
      <Link
        href={href}
        className={className}
        title={tooltip}
        aria-label={ariaLabel}
        {...(rest as Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href">)}
      >
        {content}
      </Link>
    );
  }

  return (
    <button
      className={className}
      title={tooltip}
      aria-label={ariaLabel}
      disabled={loading || (rest as ButtonHTMLAttributes<HTMLButtonElement>).disabled}
      {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}
    >
      {content}
    </button>
  );
}
