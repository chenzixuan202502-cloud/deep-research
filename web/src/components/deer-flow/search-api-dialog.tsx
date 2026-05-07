// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useState } from "react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "~/components/ui/dialog";
import { setSearchProvider, useSettingsStore } from "~/core/store";
import { cn } from "~/lib/utils";

import { Tooltip } from "./tooltip";

const SEARCH_PROVIDERS = [
  {
    value: "infoquest" as const,
    label: "InfoQuest",
  },
  {
    value: "tavily" as const,
    label: "Tavily",
  },
];

export function SearchApiDialog() {
  const [open, setOpen] = useState(false);
  const currentProvider = useSettingsStore(
    (state) => state.general.searchProvider,
  );

  const handleChange = (provider: "infoquest" | "tavily") => {
    setSearchProvider(provider);
    setOpen(false);
  };

  const currentProviderLabel =
  SEARCH_PROVIDERS.find(p => p.value === currentProvider)?.label ?? "InfoQuest";


  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Tooltip
        className="max-w-60" 
        title={
          <div>
            <span className="font-bold">Search API:</span>
            <br/>
            {currentProviderLabel}
          </div>
        }
      >
        <DialogTrigger asChild>
          <Button
            className="!border-brand !text-brand rounded-2xl"
            variant="outline"
          >
            Search API
          </Button>
        </DialogTrigger>
      </Tooltip>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>选择 Search API</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3 py-4">
          {SEARCH_PROVIDERS.map((provider) => {
            const isSelected = currentProvider === provider.value;
            return (
              <button
                key={provider.value}
                className={cn(
                  "hover:bg-accent flex items-center justify-between rounded-lg border p-3 text-left text-sm transition-colors",
                  isSelected && "border-primary bg-accent",
                )}
                onClick={() => handleChange(provider.value)}
              >
                <span>{provider.label}</span>
                {isSelected && (
                  <span className="text-primary text-xs">Current</span>
                )}
              </button>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}

