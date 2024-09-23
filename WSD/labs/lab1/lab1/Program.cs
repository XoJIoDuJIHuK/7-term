using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddDistributedMemoryCache(); // Adds a default in-memory implementation of IDistributedCache
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(20); // Set session timeout
    options.Cookie.HttpOnly = true; // Make the session cookie HTTP only
    options.Cookie.IsEssential = true; // Ensure the session cookie is always sent
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

#region xd
//List<int> getStack(HttpContext context)
//{
//    var stackJson = context.Session.GetString("stack");
//    var stack = string.IsNullOrEmpty(stackJson) ? new List<int>() : JsonSerializer.Deserialize<List<int>>(stackJson);
//    return stack;
//}

//void setStack(HttpContext context, List<int> stack)
//{
//    context.Session.SetString("stack", JsonSerializer.Serialize(stack));
//}

//app.MapGet("/api/Stack", (HttpContext context) =>
//{
//    var result = context.Session.GetInt32("result") ?? 0;
//    var stack = getStack(context);
//    int client_result = stack.Count > 0 ? result + stack[^1] : result;
//    return Results.Ok(new { result = client_result });
//});

//app.MapGet("/api/Stack/stack", (HttpContext context) =>
//{
//    var stack = getStack(context);
//    return Results.Ok(new { result = stack.ToArray() });
//});

//app.MapPost("/api/Stack", (HttpContext context, int RESULT) =>
//{
//    context.Session.SetInt32("result", RESULT);
//    return Results.Ok();
//});

//app.MapPut("/api/Stack", (HttpContext context, int ADD) =>
//{
//    var stack = getStack(context);
//    stack.Add(ADD);
//    setStack(context, stack);
//    return Results.Ok();
//});

//app.MapDelete("/api/Stack", (HttpContext context) =>
//{
//    var stack = getStack(context);

//    if (stack.Count > 0)
//    {
//        stack.RemoveAt(stack.Count - 1);
//        setStack(context, stack);
//    }

//    return Results.Ok();
//});
#endregion

app.Map("/api/Stack", async (HttpContext context) =>
{
    var method = context.Request.Method;
    var query = context.Request.Query;

    // Retrieve the existing stack and result from the session
    List<int> getStack()
    {
        var stackJson = context.Session.GetString("stack");
        return string.IsNullOrEmpty(stackJson) ? new List<int>() : JsonSerializer.Deserialize<List<int>>(stackJson);
    }

    void setStack(List<int> stack)
    {
        context.Session.SetString("stack", JsonSerializer.Serialize(stack));
    }

    int? getResult()
    {
        return context.Session.GetInt32("result");
    }

    void setResult(int result)
    {
        context.Session.SetInt32("result", result);
    }

    if (method == HttpMethods.Get)
    {
        var result = getResult() ?? 0;
        var stack = getStack();
        int clientResult = stack.Count > 0 ? result + stack[^1] : result;
        await context.Response.WriteAsJsonAsync(new { result = clientResult });
    }
    else if (method == HttpMethods.Post)
    {
        if (query.ContainsKey("result"))
        {
            int result;
            if (int.TryParse(query["result"], out result))
            {
                setResult(result);
                context.Response.StatusCode = StatusCodes.Status200OK;
            }
            else
            {
                context.Response.StatusCode = StatusCodes.Status400BadRequest;
            }
        }
        else
        {
            context.Response.StatusCode = StatusCodes.Status400BadRequest;
        }
    }
    else if (method == HttpMethods.Put)
    {
        if (query.ContainsKey("add"))
        {
            if (int.TryParse(query["add"], out int add))
            {
                var stack = getStack();
                stack.Add(add);
                setStack(stack);
                context.Response.StatusCode = StatusCodes.Status200OK;
            }
            else
            {
                context.Response.StatusCode = StatusCodes.Status400BadRequest;
            }
        }
        else
        {
            context.Response.StatusCode = StatusCodes.Status400BadRequest;
        }
    }
    else if (method == HttpMethods.Delete)
    {
        var stack = getStack();
        if (stack.Count > 0)
        {
            stack.RemoveAt(stack.Count - 1);
            setStack(stack);
        }
        context.Response.StatusCode = StatusCodes.Status200OK;
    }
    else
    {
        context.Response.StatusCode = StatusCodes.Status405MethodNotAllowed;
    }
});



app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();
app.UseSession(); // Enable session middleware

app.MapControllers(); // Map controllers

app.Run();
