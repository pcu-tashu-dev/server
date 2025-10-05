module.exports = {
  ok: (e, data = {}, status = 200) => {
    return e.json(status, { success: true, ...data });
  },

  fail: (e, message = "Bad request", status = 400) => {
    return e.json(status, { success: false, error: message });
  },
};
