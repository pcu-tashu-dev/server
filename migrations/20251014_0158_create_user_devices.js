migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("user_devices");
      return;
    } catch (_) {}

    const col = new Collection({
      type: "base",
      name: "user_devices",
      listRule: "user = @request.auth.id",
      viewRule: "user = @request.auth.id",
      updateRule: "user = @request.auth.id",
      createRule: '@request.auth.id != ""',
      deleteRule: "user = @request.auth.id",

      fields: [
        {
          type: "relation",
          name: "user",
          required: true,
          collectionId: "_pb_users_auth_",
          cascadeDelete: true,
          minSelect: 1,
          maxSelect: 1,
        },
        {
          type: "text",
          name: "token",
          required: true,
          max: 4096,
          presentable: true,
        },
        {
          type: "select",
          name: "platform",
          values: ["ios", "android", "web"],
          required: true,
        },
        {
          type: "select",
          name: "provider",
          values: ["fcm", "apns", "webpush"],
          required: true,
        },
        { type: "bool", name: "is_active", required: true, default: true },
        { type: "text", name: "app_version", max: 64 },
        { type: "text", name: "locale", max: 16 },
        { type: "date", name: "last_seen" },
      ],

      indexes: [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_devices_token ON user_devices (token)",
        "CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices (user)",
      ],
    });

    app.save(col);
  },
  (app) => {
    try {
      const c = app.findCollectionByNameOrId("user_devices");
      app.delete(c);
    } catch (_) {}
  }
);
