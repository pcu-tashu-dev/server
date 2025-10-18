migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("notifications");
      return;
    } catch (_) {}

    const collection = new Collection({
      name: "notifications",
      type: "base",
      listRule: "user = @request.auth.id",
      viewRule: "user = @request.auth.id",
      updateRule: "user = @request.auth.id",
      createRule: "",
      deleteRule: "",

      fields: [
        {
          type: "relation",
          name: "user",
          required: true,
          collectionId: "_pb_users_auth_",
          cascadeDelete: false,
          minSelect: 1,
          maxSelect: 1,
        },
        {
          type: "text",
          name: "title",
          required: true,
          max: 200,
          presentable: true,
        },
        {
          type: "text",
          name: "body",
          required: true,
          max: 2000,
          presentable: true,
        },
        {
          type: "select",
          name: "type",
          required: true,
          values: ["info", "warning", "error", "success"],
          presentable: true,
        },
        {
          type: "json",
          name: "data",
        },
        {
          type: "bool",
          name: "read",
          required: true,
          presentable: true,
          default: false,
        },
      ],

      indexes: [
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications (user, read)",
      ],
    });

    app.save(collection);
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("notifications");
      app.delete(col);
    } catch (_) {}
  }
);
