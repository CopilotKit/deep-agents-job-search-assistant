"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import type { ToolActionArgs, TodoItem, JobPosting } from "@/lib/types";

interface WriteTodosArgs {
  todos: TodoItem[];
}

interface SetPlanArgs {
  plan: string;
}

interface SetStepArgs {
  step: string;
}

interface UpdateJobsListArgs {
  jobs: JobPosting[];
}

interface AppendCoverLetterArgs {
  title: string;
  letter: string;
}

export function ToolRenderers() {
  // Handle write_todos
  useCopilotAction({
    name: "write_todos",
    description: "Create a task list",
    parameters: [
      {
        name: "todos",
        type: "object[]",
        required: true,
        attributes: [
          { name: "content", type: "string", required: true },
          { name: "status", type: "string", required: true },
        ],
      },
    ],
    handler: async (args: WriteTodosArgs) => {
      console.log("[TOOL] write_todos:", args.todos);
      return {};
    },
  });

  // Handle set_plan
  useCopilotAction({
    name: "set_plan",
    description: "Display the plan",
    parameters: [{ name: "plan", type: "string", required: true }],
    handler: async (args: SetPlanArgs) => {
      console.log("[TOOL] set_plan");
      return {};
    },
  });

  // Handle set_step
  useCopilotAction({
    name: "set_step",
    description: "Update progress step",
    parameters: [
      {
        name: "step",
        type: "string",
        required: true,
        description: "planning, searching, generating, or done",
      },
    ],
    handler: async (args: SetStepArgs) => {
      console.log("[TOOL] set_step:", args.step);
      return {};
    },
  });

  // Handle update_jobs_list
  useCopilotAction({
    name: "update_jobs_list",
    description: "Update jobs list",
    parameters: [
      {
        name: "jobs",
        type: "object[]",
        required: true,
        attributes: [
          { name: "company", type: "string" },
          { name: "title", type: "string" },
          { name: "location", type: "string" },
          { name: "url", type: "string" },
        ],
      },
    ],
    handler: async (args: UpdateJobsListArgs) => {
      console.log("[TOOL] update_jobs_list:", args.jobs.length);
      return {};
    },
  });

  // Handle append_cover_letter
  useCopilotAction({
    name: "append_cover_letter",
    description: "Append cover letter",
    parameters: [
      { name: "title", type: "string", required: true },
      { name: "letter", type: "string", required: true },
    ],
    handler: async (args: AppendCoverLetterArgs) => {
      console.log("[TOOL] append_cover_letter:", args.title);
      return {};
    },
  });

  return null;
}