import { describe, expect, test } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dir, "..");
const repoRoot = resolve(import.meta.dir, "../../..");

describe("@thinkscape/claude-thermos integration", () => {
	test("has a valid Claude plugin manifest", () => {
		const manifest = JSON.parse(readFileSync(join(root, ".claude-plugin/plugin.json"), "utf8")) as {
			name: string;
			commands: string[];
			agents: string[];
			skills?: string;
		};
		expect(manifest.name).toBe("thermos");
		expect(manifest.commands).toContain("./commands/run.md");
		expect(manifest.skills).toBeUndefined();
		expect(manifest.agents).toContain("./agents/thermo-nuclear-review-subagent.md");
	});

	test("is listed in the repo Claude marketplace", () => {
		const marketplace = JSON.parse(readFileSync(join(repoRoot, ".claude-plugin/marketplace.json"), "utf8")) as {
			name: string;
			plugins: Array<{ name: string; version: string; source: { source: string; package: string } }>;
		};
		const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf8")) as { version: string };
		const entry = marketplace.plugins.find((plugin) => plugin.name === "thermos");

		expect(marketplace.name).toBe("agent-thermos");
		expect(entry?.version).toBe(pkg.version);
		expect(entry?.source.source).toBe("npm");
		expect(entry?.source.package).toBe("@thinkscape/claude-thermos");
	});

	test("run command is concise and points to thermos agents", () => {
		const command = readFileSync(join(root, "commands/run.md"), "utf8");
		expect(command).toContain("description: Run deep correctness/security");
		expect(command).toContain("Usage: `/thermos:run");
		expect(command).toContain("thermos:thermo-nuclear-review-subagent");
		expect(existsSync(join(root, "commands/thermos.md"))).toBe(false);
		expect(existsSync(join(root, "skills"))).toBe(false);
	});

	test("installs standalone /thermos shim without API keys", () => {
		const dir = mkdtempSync(join(tmpdir(), "claude-thermos-"));
		try {
			const result = Bun.spawnSync({
				cmd: ["node", join(root, "bin/claude-thermos.js"), "install-command", "--scope", "project", "--cwd", dir],
				stdout: "pipe",
				stderr: "pipe",
			});
			expect(result.exitCode).toBe(0);
			const shim = readFileSync(join(dir, ".claude/commands/thermos.md"), "utf8");
			expect(shim).toBe(readFileSync(join(root, "shims/thermos.md"), "utf8"));
		} finally {
			rmSync(dir, { recursive: true, force: true });
		}
	});

	test("rejects install-command options without values before writing", () => {
		for (const args of [["--cwd"], ["--scope"], ["--cwd", "--dry-run"]]) {
			const dir = mkdtempSync(join(tmpdir(), "claude-thermos-invalid-"));
			try {
				const result = Bun.spawnSync({
					cmd: ["node", join(root, "bin/claude-thermos.js"), "install-command", ...args],
					cwd: dir,
					stdout: "pipe",
					stderr: "pipe",
				});
				expect(result.exitCode).not.toBe(0);
				expect(existsSync(join(dir, ".claude"))).toBe(false);
			} finally {
				rmSync(dir, { recursive: true, force: true });
			}
		}
	});
});
