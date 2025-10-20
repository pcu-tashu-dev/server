migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("daejeon_zones");
      return;
    } catch (_) {}

    const col = new Collection({
      type: "base",
      name: "daejeon_zones",

      listRule: "",
      viewRule: "",
      createRule: "",
      updateRule: "",
      deleteRule: "",

      fields: [
        {
          type: "text",
          name: "zone_id",
          required: true,
          max: 32,
          presentable: true,
          unique: true,
        },
        { type: "number", name: "min_lat", required: true },
        { type: "number", name: "max_lat", required: true },
        { type: "number", name: "min_lon", required: true },
        { type: "number", name: "max_lon", required: true },
      ],

      indexes: [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_daejeon_zones_zone_id ON daejeon_zones (zone_id)",
      ],
    });

    app.save(col);

    // seed 56 grid records (7 x 8)
    const c = app.findCollectionByNameOrId("daejeon_zones");
    const data = [
      {
        zone_id: "1-1",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "1-2",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "1-3",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "1-4",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "1-5",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "1-6",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "1-7",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "1-8",
        min_lat: 36.2,
        max_lat: 36.242857,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "2-1",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "2-2",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "2-3",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "2-4",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "2-5",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "2-6",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "2-7",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "2-8",
        min_lat: 36.242857,
        max_lat: 36.285714,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "3-1",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "3-2",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "3-3",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "3-4",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "3-5",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "3-6",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "3-7",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "3-8",
        min_lat: 36.285714,
        max_lat: 36.328571,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "4-1",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "4-2",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "4-3",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "4-4",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "4-5",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "4-6",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "4-7",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "4-8",
        min_lat: 36.328571,
        max_lat: 36.371429,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "5-1",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "5-2",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "5-3",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "5-4",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "5-5",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "5-6",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "5-7",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "5-8",
        min_lat: 36.371429,
        max_lat: 36.414286,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "6-1",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "6-2",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "6-3",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "6-4",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "6-5",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "6-6",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "6-7",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "6-8",
        min_lat: 36.414286,
        max_lat: 36.457143,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
      {
        zone_id: "7-1",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.2,
        max_lon: 127.2375,
      },
      {
        zone_id: "7-2",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.2375,
        max_lon: 127.275,
      },
      {
        zone_id: "7-3",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.275,
        max_lon: 127.3125,
      },
      {
        zone_id: "7-4",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.3125,
        max_lon: 127.35,
      },
      {
        zone_id: "7-5",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.35,
        max_lon: 127.3875,
      },
      {
        zone_id: "7-6",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.3875,
        max_lon: 127.425,
      },
      {
        zone_id: "7-7",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.425,
        max_lon: 127.4625,
      },
      {
        zone_id: "7-8",
        min_lat: 36.457143,
        max_lat: 36.5,
        min_lon: 127.4625,
        max_lon: 127.5,
      },
    ];

    for (const item of data) {
      const rec = new Record(c);
      rec.set("zone_id", item.zone_id);
      rec.set("min_lat", item.min_lat);
      rec.set("max_lat", item.max_lat);
      rec.set("min_lon", item.min_lon);
      rec.set("max_lon", item.max_lon);
      app.save(rec);
    }
  },
  (app) => {
    try {
      const c = app.findCollectionByNameOrId("daejeon_zones");
      app.delete(c);
    } catch (_) {}
  }
);
