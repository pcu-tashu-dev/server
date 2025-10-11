routerAdd("POST", "/users/duplicate/{param}", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  try {
    const param = e.request.pathValue("param");
    const query = e.request.url.query().get("data");

    if (param != "username" && param != "email") {
      return fail(e, "param must be 'username' or 'email'", 400);
    }

    if (!query) {
      return fail(
        e,
        `${param}'s value not founded. Usage: ${param}?data=your-data`,
        400
      );
    }

    let user;
    try {
      user = $app.findFirstRecordByData("users", param, query);
    } catch (error) {
      if (!(error instanceof GoError)) {
        return fail(e, error.message);
      }
    }

    if (user) {
      return fail(e, `'${query}' '${param}' already taken`, 409);
    } else {
      return ok(e, { message: `'${query}' '${param}' data can be used` }, 200);
    }
  } catch (err) {
    return fail(e, err.message);
  }
});
