import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

async function notify(title: string, body: string) {
  const { execSync } = await import("node:child_process");

  if (process.platform === "darwin") {
    execSync(
      `osascript -e 'display notification "${body.replace(/"/g, '\\"')}" with title "${title.replace(/"/g, '\\"')}" sound name "Ping"'`,
      { stdio: "ignore", timeout: 2000 },
    );
    return;
  }

  if (process.platform === "linux") {
    try {
      execSync(`notify-send "${title}" "${body}"`, {
        stdio: "ignore",
        timeout: 2000,
      });
      return;
    } catch {
      // fall through to terminal escape
    }
  }

  // Fallback: terminal OSC 777 (Ghostty, iTerm2, WezTerm, rxvt-unicode)
  process.stdout.write(`\x1b]777;notify;${title};${body}\x07`);
}

export default function (pi: ExtensionAPI) {
  pi.on("agent_settled", async () => {
    notify("Pi", "Ready");
  });
}
