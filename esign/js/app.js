"use strict";

rpc.exports = {
  add(a, b) {
    return a + b;
  },
  sub(a, b) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(a - b);
      }, 100);
    });
  },
  alert(title, message) {
    const UIAlertController = ObjC.classes.UIAlertController;
    const UIAlertAction = ObjC.classes.UIAlertAction;
    const UIApplication = ObjC.classes.UIApplication;
    var handler = new ObjC.Block({
      retType: "void",
      argTypes: ["object"],
      implementation: function () {},
    });
    ObjC.schedule(ObjC.mainQueue, function () {
      var alert =
        UIAlertController.alertControllerWithTitle_message_preferredStyle_(
          title,
          message,
          1
        );
      var defaultAction = UIAlertAction.actionWithTitle_style_handler_(
        "OK",
        0,
        handler
      );
      alert.addAction_(defaultAction);
      UIApplication.sharedApplication()
        .keyWindow()
        .rootViewController()
        .presentViewController_animated_completion_(alert, true, NULL);
    });
  },
  installed() {
    var ws = ObjC.classes.LSApplicationWorkspace.defaultWorkspace();
    var apps = ws.allInstalledApplications();
    var result = [];
    for (var i = 0; i < apps.count(); i++) {
      var proxy = apps.objectAtIndex_(i);
      if (proxy.applicationType().toString() == "System") {
        continue;
      }
      var out = {};
      out["displayName"] = proxy.localizedName().toString();
      out["bundleIdentifier"] = proxy.bundleIdentifier().toString();
      out["bundlePath"] = proxy.bundleURL().toString();
      out["dataPath"] = [proxy.dataContainerURL(), ""].join("Documents");
      out["executablePath"] = [
        proxy.bundleURL().toString(),
        proxy.bundleExecutable().toString(),
      ].join("");
      out["vsaPath"] = "NO";
      const vsaPath = out["bundlePath"].slice(8) + "emmlib.framework/emmlib";
      var mgr = ObjC.classes.NSFileManager.defaultManager();
      const isExitVsa = mgr.fileExistsAtPath_(vsaPath).toString();
      out["vsaPath"] = isExitVsa;
      result.push(out);
    }
    return result;
  },
};
