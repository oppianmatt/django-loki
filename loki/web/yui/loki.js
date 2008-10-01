function bot_init(botname){
    YAHOO.util.Event.on(botname + "_report", "click", function(e) { 
        bot_report(botname);
        YAHOO.util.Event.preventDefault(e); 
    });
    bot_status(botname)
}

function bot_status(botname){
    // Define the callbacks for the asyncRequest
    var callbacks = {

        success : function (o) {
            // Process the JSON data returned from the server
            var r = [];
            r = YAHOO.lang.JSON.parse(o.responseText);

            var x = document.getElementById(r.botname + '_status');
            x.style.color = r.stsclr
            x.innerHTML = r.botstatus;
        }, 

        timeout : 3000
    }

    // Make the call to the server for JSON data
    YAHOO.util.Connect.asyncRequest('GET',"/json/botstatus/" + botname + "/", callbacks);
};

function bot_report(botname){
    // Define the callbacks for the asyncRequest
    var callbacks = {

        success : function (o) {
            // Process the JSON data returned from the server
            var r = [];
            r = YAHOO.lang.JSON.parse(o.responseText);
            var br = document.getElementById('master_report');
            br.style.visibility = (r.type == 'master' ? 'visible' : 'hidden');
            br = document.getElementById('slave_report');
            br.style.visibility = (r.type == 'slave' ? 'visible' : 'hidden');

            var x = document.getElementById(r.type + '_report_botname');
            x.innerHTML = r.name;
            x = document.getElementById(r.type + '_report_bottype');
            x.innerHTML = r.type.charAt(0).toUpperCase() + r.type.substr(1).toLowerCase();
            x = document.getElementById(r.type + '_report_botserver');
            x.innerHTML = 'not passed';
            x = document.getElementById(r.type + '_report_botcomments');
            x.innerHTML = r.comment;
            if(r.type == 'master') {
                x = document.getElementById(r.type + '_report_botwebport');
                x.innerHTML = r.web_port;
                x = document.getElementById(r.type + '_report_botslaveport');
                x.innerHTML = r.slave_port;
                x = document.getElementById(r.type + '_report_botslavepass');
                x.innerHTML = r.slave_passwd;
                x = document.getElementById(r.type + '_report_botconfig');
                x.innerHTML = r.config_source;
            }
            if(r.type == 'slave') {
                x = document.getElementById(r.type + '_report_botsteps');
                x.innerHTML = r.steps;
            }
        }, 

        timeout : 3000
    }

    // Make the call to the server for JSON data
    YAHOO.util.Connect.asyncRequest('GET',"/json/botreport/" + botname + "/", callbacks);
};

//an anonymous function wraps our code to keep our variables 
//in function scope rather than in the global namespace: 
//http://developer.yahoo.com/yui/examples/treeview/menu_style.html
(function() { 
    var tree; //will hold our TreeView instance 
     
    function treeInit() { 
        //instantiate the tree: 
        tree = new YAHOO.widget.TreeView("loki_tree"); 
         
        var servers = new YAHOO.widget.MenuNode("Servers", tree.getRoot(), false); 
        var masters = new YAHOO.widget.MenuNode("Master BuildBots", tree.getRoot(), false); 
        var slaves = new YAHOO.widget.MenuNode("Slave BuildBot", tree.getRoot(), false); 
        //draw the built tree
        tree.draw();
         
        //handler for collapsing all nodes 
        YAHOO.util.Event.on("collapse", "click", function(e) { 
            YAHOO.log("Collapsing all TreeView  nodes.", "info", "example"); 
            tree.collapseAll(); 
            YAHOO.util.Event.preventDefault(e); 
        }); 
    } 
     
    //When the DOM is done loading, we can initialize our TreeView 
    //instance: 
    YAHOO.util.Event.onDOMReady(treeInit); 
     
})();//anonymous function wrapper closed; () notation executes function

