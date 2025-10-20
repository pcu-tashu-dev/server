migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("stations");
      return;
    } catch (_) {}
    const dz = app.findCollectionByNameOrId("daejeon_zones");

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
          name: "id",
          required: true,
        },
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
          type: "relation",
          name: "zone",
          required: true,
          collectionId: dz.id,
          maxSelect: 1,
          cascadeDelete: false,
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

    col.fields.addAt(
      0,
      new Field({
        autogeneratePattern: "",
        hidden: false,
        id: "text3208210256",
        max: 0,
        min: 0,
        name: "id",
        pattern: "^[A-z0-9]+$",
        presentable: false,
        primaryKey: true,
        required: true,
        system: true,
        type: "text",
      })
    );
  },

  (app) => {
    try {
      const col = app.findCollectionByNameOrId("stations");
      app.delete(col);
    } catch (_) {}
  }
);
