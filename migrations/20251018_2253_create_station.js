migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("stations");
      return;
    } catch (_) {}

    const col = new Collection({
      type: "base",
      name: "stations",

      listRule: "",
      viewRule: "",
      createRule: "",
      updateRule: "",
      deleteRule: "",

      fields: [
        {
          type: "text",
          name: "name",
          required: true,
        },
        {
          type: "number",
          name: "lat",
          required: true,
        },
        {
          type: "number",
          name: "lon",
          required: true,
        },
        {
          type: "text",
          name: "address",
          required: true,
        },
        {
          type: "autodate",
          name: "created",
          required: false,
          onCreate: true,
        },
        {
          type: "autodate",
          name: "updated",
          required: false,
          onUpdate: true,
        },
      ],

      indexes: [],
    });

    app.save(col);
  },

  (app) => {
    try {
      const col = app.findCollectionByNameOrId("stations");
      app.delete(col);
    } catch (_) {}
  }
);
