export type Step = "idle" | "planning" | "searching" | "generating" | "done";

export type JobPosting = {
  company: string;
  title: string;
  location: string;
  url: string;
  goodMatch?: string;
};

export type TodoItem = {
  content: string;
  status: string;
};

export type AgentState = {
  step: Step;
  // plan: string;
  jobs_list: JobPosting[];
  // cover_letter_title: string;
  cover_letter_append?: string;
  [key: string]: unknown;
};

export type ToolActionArgs = {
  todos?: TodoItem[];
  plan?: string;
  step?: Step;
  jobs?: JobPosting[];
  title?: string;
  letter?: string;
};
