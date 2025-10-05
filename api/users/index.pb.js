routerAdd("POST", "/users", (e) => {
  try {
    const data = new DynamicModel({
      email: "",
      username: "",
      password: "",
      passwordConfirm: "",
    });
    e.bindBody(data);
    const email = data.email;
    const username = data.username;
    const password = data.password;
    const passwordConfirm = data.passwordConfirm;

    if (!email || !password || !passwordConfirm) {
      return e.json(400, {
        success: false,
        error: "email, password, passwordConfirm are required",
      });
    }

    if (password !== passwordConfirm) {
      return e.json(400, { success: false, error: "passwords do not match" });
    }

    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return e.json(400, { success: false, error: "invalid email format" });
    }

    // email 중복 검사
    let dupEmail = null;
    try {
      dupEmail = $app.findFirstRecordByData("users", "email", email);
    } catch (_) {
      // Not Found -> OK
    }
    if (dupEmail) {
      return e.json(400, { success: false, error: "email already registered" });
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
        return e.json(400, { success: false, error: "username already taken" });
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

    return e.json(201, { success: true, user: user.publicExport() });
  } catch (err) {
    const msg = err?.message || "Failed to register";
    return e.json(500, { success: false, error: msg });
  }
});

routerAdd("POST", "/users/login", (e) => {
  try {
    const data = new DynamicModel({
      email: "",
      password: "",
    });
    e.bindBody(data);
    const email = data.email;
    const password = data.password;

    if (!email || !password) {
      return e.json(400, {
        success: false,
        error: "email, password are required",
      });
    }
    let user;

    try {
      user = $app.findFirstRecordByData("users", "email", email);
    } catch (error) {
      return e.json(500, {
        success: false,
        error: error.message,
      });
    }

    if (!user.validatePassword(password)) {
      return e.json(401, {
        success: false,
        error: "email or password is incorrect",
      });
    }

    const token = user.newAuthToken();
    return e.json(200, {
      success: true,
      token: { access_token: token, token_type: "Bearer" },
      user: {
        id: user.id,
        email: user.email(),
        username: user.getString("username"),
      },
    });
  } catch (err) {
    const msg = err?.message || "Failed to login";
    return e.json(500, { success: false, error: msg });
  }
});
