import ContentTools from "ContentTools";

// CoffeScript function for subclassing. Blatantly copied from ContentTools
// build.
const __hasProp = {}.hasOwnProperty;
const __extends = function(child, parent) {
    for (var key in parent) {
        if (__hasProp.call(parent, key)) child[key] = parent[key];
    }
    function ctor() {
        this.constructor = child;
    }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor();
    child.__super__ = parent.prototype;
    return child;
};

window.addEventListener("load", function() {
    // We add three more tools to the ContentTools editor.
    // Strike allows to strikethrough the text.
    ContentTools.Tools.Strike = (function(_super) {
        __extends(Strike, _super);

        function Strike() {
            return Strike.__super__.constructor.apply(this, arguments);
        }
        ContentTools.ToolShelf.stow(Strike, "strike");
        Strike.label = "Strike";
        Strike.icon = "strike";
        Strike.tagName = "s";

        return Strike;
    })(ContentTools.Tools.Bold);

    // Red colours the text red. We introduce a tag <red> for this.
    ContentTools.Tools.Red = (function(_super) {
        __extends(Red, _super);

        function Red() {
            return Red.__super__.constructor.apply(this, arguments);
        }
        ContentTools.ToolShelf.stow(Red, "red");
        Red.label = "Red";
        Red.icon = "red";
        Red.tagName = "red";

        return Red;
    })(ContentTools.Tools.Bold);

    // Green colours the text green.
    ContentTools.Tools.Green = (function(_super) {
        __extends(Green, _super);

        function Green() {
            return Green.__super__.constructor.apply(this, arguments);
        }
        ContentTools.ToolShelf.stow(Green, "green");
        Green.label = "Green";
        Green.icon = "green";
        Green.tagName = "green";

        return Green;
    })(ContentTools.Tools.Bold);

    ContentTools.DEFAULT_TOOLS = [["bold", "strike", "red", "green", "undo", "redo"]];

    const editor = ContentTools.EditorApp.get();
    editor.init("[data-editable]", "data-name");
});
