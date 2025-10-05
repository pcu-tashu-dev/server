routerAdd("POST", "/users/login", (e) => {
  try {
    const { ok, fail } = require(`${__hooks}/lib/response.js`);
    const { parse, requireFields } = require(`${__hooks}/lib/body.js`);
    const body = parse(e, { email: "", password: "" });
    requireFields(body, ["email", "password"]);

    const email = body.email.trim();
    const password = body.password;

    let user;

    try {
      user = $app.findFirstRecordByData("users", "email", email);
    } catch (error) {
      return fail(e, error.message);
    }

    if (!user.validatePassword(password)) {
      return fail(e, "email or password is incorrect", 401);
    }

    const token = user.newAuthToken();
    return ok(e, {
      token: { access_token: token, token_type: "Bearer" },
      user: {
        id: user.id,
        email: user.email(),
        username: user.getString("username"),
      },
    });
  } catch (err) {
    return fail(e, err.message);
  }
});
