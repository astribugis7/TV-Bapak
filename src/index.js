export default {
  async fetch(request, env, ctx) {
    const githubToken = env.GITHUB_TOKEN;

    const url = "https://api.github.com/repos/astribugis7/TV-Bapak/contents/oantek.m3u";

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: "application/vnd.github.v3.raw",
        "User-Agent": "cloudflare-worker"
      }
    });

    if (!res.ok) {
      return new Response(`# Error: ${res.status} - ${res.statusText}`, { status: res.status });
    }

    const m3uContent = await res.text();

    return new Response(m3uContent, {
      headers: {
        "Content-Type": "audio/x-mpegurl; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
};
