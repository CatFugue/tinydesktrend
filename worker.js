// Deployed to the "tinydesktrend" Worker (assets binding ASSETS, run_worker_first: true,
// html_handling: auto-trailing-slash, not_found_handling: 404-page).
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.hostname === 'www.tinydesktrend.com') {
      u.hostname = 'tinydesktrend.com';
      return Response.redirect(u.toString(), 301);
    }
    const r = await env.ASSETS.fetch(req);
    // Asset handler issues 307 for slashless directory URLs; make them permanent.
    if (r.status === 307 || r.status === 308) {
      const loc = r.headers.get('Location');
      if (loc) return Response.redirect(new URL(loc, u).toString(), 301);
    }
    const h = new Headers(r.headers);
    h.set('X-Content-Type-Options', 'nosniff');
    h.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    h.set('X-Frame-Options', 'DENY');
    h.set('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'none'; frame-ancestors 'none'; base-uri 'self'");
    return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
  },
};
