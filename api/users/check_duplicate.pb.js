routerAdd("POST", "/users/duplicate/{param}", (e) => {
  const { ok, fail } = require(`${__hooks}/lib/response.js`);
  const { parse } = require(`${__hooks}/lib/body.js`);
  try {
    const param = e.request.pathValue("param");

    if (param != "username" && param != "email") {
      return fail(e, "param must be 'username' or 'email'", 400);
    }

    const body = parse(e, { data: "" }); // FIXME: body 데이터 -> Query Parameter로 변경 필요
    const data = body.data;
  } catch (err) {
    return fail(e, err.message);
  }
});
