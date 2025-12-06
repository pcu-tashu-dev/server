migrate(
  (app) => {
    try {
      app.findCollectionByNameOrId("station_forecasts");
      return;
    } catch (_) {}

    const stations = app.findCollectionByNameOrId("stations");

    const col = new Collection({
      type: "base",
      name: "station_forecasts",
      listRule: "",
      viewRule: "",
      createRule: "",
      updateRule: "",
      deleteRule: "",
      fields: [
        {
          type: "relation",
          name: "station",
          required: true,
          collectionId: stations.id,
          cascadeDelete: false,
          minSelect: 1,
          maxSelect: 1,
        },
        {
          type: "date",
          name: "target_time",
          required: true,
        },
        {
          type: "number",
          name: "horizon_minutes",
          required: true,
        },
        {
          type: "number",
          name: "predicted_count",
          required: true,
        },
        {
          type: "text",
          name: "model_version",
          max: 128,
        },
        {
          type: "autodate",
          name: "created",
          onCreate: true,
        },
        {
          type: "autodate",
          name: "updated",
          onUpdate: true,
        },
      ],
      indexes: [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_station_forecasts_station_time ON station_forecasts (station, target_time)",
        "CREATE INDEX IF NOT EXISTS idx_station_forecasts_time ON station_forecasts (target_time)",
      ],
    });

    app.save(col);
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("station_forecasts");
      app.delete(col);
    } catch (_) {}
  }
);
