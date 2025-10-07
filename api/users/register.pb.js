routerAdd("POST", "/users", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse, requireFields } = require(`${__hooks}/lib/body.js`);
  try {
    const body = parse(e, {
      email: "",
      username: "",
      password: "",
      passwordConfirm: "",
    });
    requireFields(body, ["email", "username", "password", "passwordConfirm"]);

    const email = body.email;
    const username = body.username;
    const password = body.password;
    const passwordConfirm = body.passwordConfirm;

    if (password !== passwordConfirm) {
      return fail(e, "passwords don't match", 400);
    }

    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return fail(e, "invalid email format", 400);
    }

    let dupEmail = null;
    try {
      dupEmail = $app.findFirstRecordByData("users", "email", email);
    } catch (_) {
      // Not Found -> OK
    }
    if (dupEmail) {
      return fail(e, "email already registered", 409);
    }

    // username 중복 검사
    let usersCol = $app.findCollectionByNameOrId("users");
    const hasUsernameField =
      typeof usersCol?.schema?.getFieldByName === "function"
        ? !!usersCol.schema.getFieldByName("username")
        : true;

    if (hasUsernameField && username) {
      let dupUsername = null;
      try {
        dupUsername = $app.findFirstRecordByData("users", "username", username);
      } catch (_) {}
      if (dupUsername) {
        return fail(e, "username already taken", 409);
      }
    }

    const user = new Record(usersCol);
    user.set("email", email);
    user.set("password", password);
    user.set("passwordConfirm", passwordConfirm);

    if (hasUsernameField && username) {
      user.set("username", username);
    }

    $app.save(user);

    if (typeof user.hide === "function") {
      user.hide("password", "passwordConfirm", "tokenKey");
    }

    const thinUser = {
      id: user.id,
      email: user.getString("email"),
      username: user.getString("username"),
      created: user.getString("created"),
    };
    return ok(
      e,
      {
        user: thinUser,
      },
      201
    );
  } catch (err) {
    return fail(e, err.message);
  }
});
