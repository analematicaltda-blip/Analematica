import { describe, expect, test } from "bun:test";
import { thermosWorkflow } from "../src/content.ts";
import {
	renderClaudeAgent,
	renderClaudeRunCommand,
	renderClaudeShimCommand,
	renderCodexThermosSkill,
	renderPiAgent,
} from "../src/render.ts";

describe("renderers", () => {
	test("renders Codex $thermos skill", () => {
		const skill = renderCodexThermosSkill();
		expect(skill).toContain("name: thermos");
		expect(skill).toContain("$thermos");
		expect(skill).toContain(thermosWorkflow);
		expect(skill).toContain("The packaged rubric references are available");
		expect(skill).not.toContain("Before launching review passes");
	});

	test("renders Claude plugin command and shim variants", () => {
		const runCommand = renderClaudeRunCommand();
		const shimCommand = renderClaudeShimCommand();
		expect(runCommand).toContain("Usage: `/thermos:run");
		expect(shimCommand).toContain("Usage: `/thermos ");
		expect(runCommand).toContain(thermosWorkflow);
		expect(shimCommand).toContain(thermosWorkflow);
		expect(runCommand).toContain("thermos:thermo-nuclear-review-subagent");
	});

	test("renders Claude agents", () => {
		expect(renderClaudeAgent("deep")).toContain("name: thermo-nuclear-review-subagent");
		expect(renderClaudeAgent("quality")).toContain("code-judo");
	});

	test("renders Pi provider agents", () => {
		expect(renderPiAgent("deep", "nico")).toContain("systemPromptMode: replace");
		expect(renderPiAgent("quality", "gotgenes")).toContain("max_turns: 20");
		expect(renderPiAgent("quality", "tintinweb")).toContain("tools: read, grep");
	});
});
