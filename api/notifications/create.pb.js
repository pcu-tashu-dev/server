routerAdd("POST", "/notifications", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);

  try {
    if (!e.admin) return fail(e, "admin only", 403);
    const body = parse(e, {
      userId: "",
      title: "",
      body: "",
      type: "info",
      data: {},
      read: false,
    });
    requireFields(body, ["userId", "title", "body"]);

    const ntype = (body.type || "info").toLowerCase();
    const TYPE_VALUES = ["info", "warning", "error", "success"];
    if (!TYPE_VALUES.includes(ntype)) {
      return fail(e, `type must be one of: ${TYPE_VALUES.join(", ")}`, 400);
    }

    let userRec;
    try {
      userRec = $app.findRecordById("_pb_users_auth_", body.userId);
    } catch (_) {
      return fail(e, "user not found", 404);
    }

    const col = $app.findCollectionByNameOrId("notifications");
    const rec = new Record(col);
    rec.set("user", userRec.id);
    rec.set("title", String(body.title));
    rec.set("body", String(body.body));
    rec.set("type", ntype);
    rec.set("data", body.data || {});
    rec.set("read", !!body.read);

    $app.save(rec);
    try {
      const FCM_KEY = $app.getEnv("FCM_SERVER_KEY") || "";
      if (FCM_KEY) {
        const devCol = $app.findCollectionByNameOrId("user_devices");
        const tokens = $app
          .dao()
          .findRecordsByFilter(
            devCol.id,
            `user="${userRec.id}" && is_active = true`,
            "-last_seen",
            1,
            200
          )
          .map((r) => r.get("token"))
          .filter(Boolean);

        if (tokens.length) {
          const payload = {
            registration_ids: tokens,
            priority: "high",
            notification: {
              title: rec.get("title"),
              body: rec.get("body"),
            },
            data: {
              type: rec.get("type"),
              ...(rec.get("data") || {}),
              notification_id: rec.id,
            },
          };

          const res = $http.send({
            url: "https://fcm.googleapis.com/fcm/send",
            method: "POST",
            body: JSON.stringify(payload),
            headers: {
              "Content-Type": "application/json",
              Authorization: `key=${FCM_KEY}`,
            },
            timeout: 10000,
          });
        }
      }
    } catch (pushErr) {
      console.log("[notifications:create] push error:", pushErr);
    }

    return ok(e, {
      id: rec.id,
      user: rec.get("user"),
      title: rec.get("title"),
      body: rec.get("body"),
      type: rec.get("type"),
      read: rec.get("read"),
      data: rec.get("data") || {},
      created: rec.get("created"),
      updated: rec.get("updated"),
    });
  } catch (err) {
    return fail(e, err.message);
  }
});
