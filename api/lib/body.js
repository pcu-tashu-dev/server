module.exports = {
  parse: (e, defaults = {}) => {
    try {
      const parsed = (e.requestInfo && e.requestInfo().body) || {};
      return { ...defaults, ...parsed };
    } catch (_) {
      try {
        const raw = toString(e.request.body) || "";
        if (!raw.trim()) return { ...defaults };
        return { ...defaults, ...JSON.parse(raw) };
      } catch {
        throw new BadRequestError("Invalid request body");
      }
    }
  },

  requireFields: (obj, fields = []) => {
    const missing = fields.filter(
      (k) => !obj[k] || (typeof obj[k] === "string" && !obj[k].trim())
    );
    if (missing.length) {
      throw new BadRequestError(`${missing.join(", ")} are required`);
    }
    return obj;
  },
};
