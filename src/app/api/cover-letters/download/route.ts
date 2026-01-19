import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { existsSync } from "node:fs";

export async function GET() {
  const filePath = path.join(process.cwd(), "cover_letters.md");

  if (!existsSync(filePath)) {
    return NextResponse.json(
      { ok: false, error: "cover_letters.md not created yet" },
      { status: 404 }
    );
  }

  const data = await readFile(filePath, "utf8");
  return new NextResponse(data, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Content-Disposition": 'attachment; filename="cover_letters.md"',
    },
  });
}