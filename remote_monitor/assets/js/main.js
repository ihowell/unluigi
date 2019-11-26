const experiments = {};
const tasks = {};
const task_classes = {};
let active_experiment_id = null;
let active_class = "All";
let active_workflow_id = null;
let active_task_id = null;
const datetime_format = 'YYYY-MM-DD HH:mm:ss';

function fetch_experiments() {
    return fetch("/api/experiments.php")
        .then((res) =>res.json())
        .then(experiment_json => {
            experiment_json['experiments'].forEach(exp => {
                experiments[exp['experiment_id']] = exp;
            });
            console.log(experiments);
        }).catch(err => console.error);
}

function fetch_tasks(experiment_id) {
    const body = {
        experiment_id,
    };
    if (tasks[experiment_id])
        body["last_retrieved_updates"] = tasks[experiment_id]["last_retrieved_updates"];

    return fetch("/api/tasks.php", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    }).then(res => res.json())
        .then(tasks_json => {
            if (!tasks[experiment_id]) {
                tasks[experiment_id] = {};
                task_classes[experiment_id] = {};
            }
            tasks_json['tasks']
                .forEach(task => {
                    tasks[experiment_id][task['task_id']] = task;
                    task_classes[experiment_id][task['task_class']] = true;
                });
        });
}

function get_latest_experiment_id() {
    return Object.values(experiments).sort((a, b) => moment(b['created']).diff(moment(a['created'])))[0]['experiment_id'];
}

function set_experiments() {
    const data = Object.values(experiments).sort((a, b) => moment(b['created']).diff(moment(a['created'])))
          .map(d => ({
              "experiment_id": d.experiment_id,
              "created": d.created,
              "name": d.name,
              "status": d.status,
              "active": active_experiment_id === d.experiment_id,
          }));

    const key = d => d ? `${d.experiment_id}${d.active}` : this.id;
    const u = d3.select('#experiments')
          .selectAll('li')
          .data(data, key);

    const entering = u.enter()
          .append('li')
          .classed('nav-item', true)
          .classed('active', (d) => d.active)
          .on('click', d => {
              if (!d.active) {
                  set_active_experiment(d.experiment_id);
              }
          })
          .append('a')
          .classed('nav-link', true)
          .classed('active', (d) => d.active_experiment);
    entering
        .append('p')
        .text((d) => d.name)
        .append('i')
        .classed('material-icons-outlined', true)
        .classed('succeeded', d => d.status === 'succeeded')
        .classed('failed', d => d.status === 'failed')
        .classed('canceled', d => d.status === 'canceled')
        .classed('inprogress', d => d.status === null)
        .text(d => {
            if (d.status === 'succeeded')
                return 'cloud_done';
            else if (d.status === 'failed')
                return 'cloud_off';
            else if (d.status === 'canceled')
                return 'remove_circle_outline';
            else
                return 'cloud_upload';
        });

    const now = moment(moment.utc().format(datetime_format), datetime_format);
    entering
        .append('p')
        .text(d => { return `Started ${moment(d.created).from(now)}`; });

    u.exit().remove();
}

function set_classes() {
    let classes = [];
    if (active_experiment_id !== null) {
        classes = Object.keys(task_classes[active_experiment_id]).map(d => ({
            "class": d,
            "active": d === active_class,
        }));
        classes.unshift({ class: "All", active: active_class === "All" });
    }

    const key = d => d ? `${d.class}${d.active}` : this.id;
    const u = d3.select('#classes_list')
          .selectAll('li')
          .data(classes, key);

    const entering = u.enter()
          .append('li')
          .classed('nav-item', true)
          .classed('active', d => d.active)
          .on('click', d => { set_active_class(d.class); })
          .append('a')
          .classed('nav-link', true)
          .classed('active', d => d.active)
          .text(d => d.class);

    u.exit().remove();
}

function set_workflows() {
    let data = [];
    if (active_experiment_id !== null) {
        const root_task_id = experiments[active_experiment_id]['root_task_id'];
        data = tasks[active_experiment_id][root_task_id]['dependencies']
            .map(d => tasks[active_experiment_id][d])
            .map(d => ({
                "task_id": d.task_id,
                "name": d.name,
                "active": active_workflow_id === d.task_id
            }));
    }

    const key = d => d ? `${d.task_id}${d.active}` : this.id;
    const u = d3.select('#workflows')
          .selectAll('li')
          .data(data, key);

    const entering = u.enter()
          .append('li')
          .classed('nav-item', true)
          .classed('active', d => d.active)
          .on('click', d => { set_active_workflow(d.task_id); })
          .append('a')
          .classed('nav-link', true)
          .classed('active', d => d.active)
          .text(d => d.name)
          .append('div')
          .classed('ripple-container', true);

    u.exit().remove();
}

function set_tasks() {
    let data = [];
    if (active_experiment_id !== null) {
        data = Object.values(tasks[active_experiment_id])
            .map(d => ({
                task_id: d.task_id,
                name: d.name,
                active: d.task_id === active_task_id
            }));
    }

    const key = d => d ? `${d.task_id}${d.active}` : this.id;
    const u = d3.select('#tasks_list')
          .selectAll('li')
          .data(data, key);

    const entering = u.enter()
          .append('li')
          .classed('nav-item', true)
          .classed('active', d => d.active)
          .on('click', (d) => { set_active_task(d.task_id); })
          .append('a')
          .classed('nav-link', true)
          .classed('active', d => d.active)
          .text(d => d.name);

    u.exit().remove();
}

function set_task_params() {
    let data = [];
    if (active_experiment_id !== null && active_task_id !== null) {
        data = Object.entries(JSON.parse(tasks[active_experiment_id][active_task_id].task_params));
    }

    const u = d3.select('#params-table')
          .selectAll('tr')
          .data(data, d => d);

    const row = u.enter()
          .append('tr');
    row.append('td')
        .text(d => d[0]);
    row.append('td')
        .text(d => d[1]);

    u.exit().remove();
}

function set_active_experiment(experiment_id) {
    active_experiment_id = experiment_id;
    if (experiment_id === null) {
        active_experiment_id = null;
        set_classes(null);
        set_workflows(null);
        set_tasks(null);
        set_task_params(null, null);
        return;
    }

    fetch_tasks(experiment_id)
        .then(() => {
            set_experiments();
            set_active_class("All");
            set_active_workflow(null);
            set_active_task(experiments[experiment_id].root_task_id);
        });
}

function set_active_class(task_class) {
    active_class = task_class;
    set_classes();
}

function set_active_workflow(workflow_id) {
    active_workflow_id = workflow_id;
    set_workflows();
}

function set_active_task(task_id) {
    active_task_id = task_id;
    set_tasks();
    set_task_params();
}

fetch_experiments()
    .then(() => {
        if (experiments.length > 0) {
            const experiment_id = get_latest_experiment_id();
            return set_active_experiment(experiment_id);
        }
    });


function getTreeList(result_obj) {
    var tree = [];

    for (i = 0; i < result_obj.tasks.length; i++) {
        var id = result_obj.tasks[i].task_id;
        var children = result_obj.tasks[i].dependencies;

        if (i == 0) {
            var cur_child = {};
            cur_child.name = result_obj.tasks[i].name;
            cur_child.id = id;
            tree.push(cur_child);
        }
        //console.log("idx: ", i);
        if (children != undefined) {
            //console.log(children.length);

            for (j = 0; j < children.length; j++) {
                //console.log("in: ", j);
                var cur_child = {};
                for (k = 0; k < result_obj.tasks.length; k++) {
                    if (result_obj.tasks[k].task_id == children[j]) {
                        cur_child.name = result_obj.tasks[k].name;
                    }
                }
                //cur_child.name = children[j];
                cur_child.id = children[j];
                cur_child.parentId = id;
                tree.push(cur_child);
            }
        }
        /*else {
          var cur_child = {};
          cur_child.text = id;
          cur_child.id = id;
          tree.push(cur_child);
          }*/
    }
    return tree;
}



var result_string = '{"tasks":[{"task_id":1,"experiment_id":1,"name":"Root Task","task_class":"scheduler","status":"Pending","start_time":null,"end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:01.992051","dependencies":[2,5,8]},{"task_id":2,"experiment_id":1,"name":"Workflow 1","task_class":"workflow","status":"Pending","start_time":null,"end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:01.993470","dependencies":[3]},{"task_id":3,"experiment_id":1,"name":"Calculate 1","task_class":"calculate","status":"InProgress","start_time":"2019-10-31 15:37:01.991279","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:01.995305","dependencies":[4]},{"task_id":4,"experiment_id":1,"name":"Parse 1","task_class":"parse","status":"Complete","start_time":"2019-10-31 15:07:01.991261","end_time":"2019-10-31 15:37:01.991279","output_or_error":null,"last_updated":"2019-10-31 16:07:01.997327"},{"task_id":5,"experiment_id":1,"name":"Workflow 2","task_class":"workflow","status":"Pending","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:01.998666","dependencies":[6]},{"task_id":6,"experiment_id":1,"name":"Calculate 2","task_class":"calculate","status":"Pending","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:02.000104","dependencies":[7]},{"task_id":7,"experiment_id":1,"name":"Parse 2","task_class":"parse","status":"Complete","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:02.001776"},{"task_id":8,"experiment_id":1,"name":"Workflow 3","task_class":"workflow","status":"Pending","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:02.003118","dependencies":[9]},{"task_id":9,"experiment_id":1,"name":"Calculate 3","task_class":"calculate","status":"Pending","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:02.004451","dependencies":[10]},{"task_id":10,"experiment_id":1,"name":"Parse 3","task_class":"parse","status":"Complete","start_time":"2019-10-31 15:07:01.991261","end_time":null,"output_or_error":null,"last_updated":"2019-10-31 16:07:02.005631"}],"last_retrieved_updates":1572538087}'

var result_obj = JSON.parse(result_string);

var root = getTree(result_obj);
var root_2 = getTreeList(result_obj);


// reordering list
final_list = []
root.all(function (node){
    //console.log(node.model.id);
    //console.log(node.model);
    for (i = 0; i < root_2.length; i++) {
        if (node.model.id == root_2[i].id) {
            final_list.push(root_2[i]);
        }
    }
});

console.log(final_list);

var arr = final_list,
    data = arr.reduce(function (r, a) {
        function getParent(s, b) {
            return b.id === a.parentId ? b : (b.children && b.children.reduce(getParent, s));
        }

        var index = 0, node;
        if ('parentId' in a) {
            node = r.reduce(getParent, {});
        }
        if (node && Object.keys(node).length) {
            node.children = node.children || [];
            node.children.push(a);
        } else {
            while (index < r.length) {
                if (r[index].parentId === a.id) {
                    a.children = (a.children || []).concat(r.splice(index, 1));
                } else {
                    index++;
                }
            }
            r.push(a);
        }
        return r;
    }, []);




function getTree(result_obj) {
    var tree = new TreeModel();
    var root = tree.parse({id: result_obj.tasks[0].task_id, children:[]});

    for (i = 0; i < result_obj.tasks.length; i++) {
        var id = result_obj.tasks[i].task_id;
        //var cur_root_node = tree.parse({id: id, children: []});
        var cur_root_node = root.first(function (node) {
            return node.model.id === id;
        });
        //if (i == 0) {root = cur_root_node;}
        var child_idx_list = result_obj.tasks[i].dependencies;
        if (child_idx_list != undefined) {
            console.log(i, id, child_idx_list);
            for (var j = 0; j < child_idx_list.length; j++) {
                //console.log("adding: ", child_idx_list[j], "to node: ", id);
                var cur_child_node = tree.parse({id: child_idx_list[j], children: []});
                //console.log("cur_child_node", cur_child_node);
                cur_root_node.addChild(cur_child_node);
            }
        }
    }
    return root;
}



var treeData = [
    {
        "name": "Job 0",
        "parent": "null",
        "children": [
            {
                "name": "Process 1",
                "parent": "Job 0",
                "children": [
                    {
                        "name": "Process 3",
                        "parent": "Process 1"
                    },
                    {
                        "name": "Process 4",
                        "parent": "Process 2"
                    }
                ]
            },
            {
                "name": "Process 2",
                "parent": "Job 0"
            }
        ]
    },
    {
        "name": "Job 1",
        "parent": "null",
        "children": [
            {
                "name": "Process 1",
                "parent": "Job 1",
            },
            {
                "name": "Process 2",
                "parent": "Job 1",
                "children": [
                    {
                        "name": "Process 3",
                        "parent": "Process 2"
                    },
                    {
                        "name": "Process 4",
                        "parent": "Process 2"
                    }
                ]
            }
        ]
    },
    {
        "name": "Job 2",
        "parent": "null",
        "children": [
            {
                "name": "Process 1",
                "parent": "Job 2",
                "children": [
                    {
                        "name": "Process 3",
                        "parent": "Process 1"
                    },
                    {
                        "name": "Process 4",
                        "parent": "Process 2"
                    }
                ]
            },
            {
                "name": "Process 2",
                "parent": "Job 2"
            }
        ]
    },
    {
        "name": "Job 3",
        "parent": "null",
        "children": [
            {
                "name": "Process 1",
                "parent": "Job 3",
            },
            {
                "name": "Process 2",
                "parent": "Job 3",
                "children": [
                    {
                        "name": "Process 3",
                        "parent": "Process 2"
                    },
                    {
                        "name": "Process 4",
                        "parent": "Process 2"
                    }
                ]
            }
        ]
    }
];

treeData = data;

/*
  var listing = document.getElementById("listing");
  var x = document.createElement("BUTTON");
  var t = document.createTextNode("Click me");
  x.appendChild(t);
  listing.appendChild(x);
*/

function addButton(index) {
    var element = document.createElement("input");
    //Assign different attributes to the element.
    element.type = "button";
    element.className = "btn btn-primary btn-block"
    element.value = "Job " + index; // Really? You want the default value to be the type string?
    element.name = "hehe"; // And the name too?
    element.onclick = function() { // Note this is a function
        drawTree(index);
    };

    var foo = document.getElementById("listing");
    //Append the element in page (in span).
    foo.appendChild(element);
}

var i;
console.log("----------tree length: ", treeData.length)
for (i = 0; i < treeData.length; i++) {
    console.log(i)
    addButton(i);
}

function drawTree(index) {
    root = treeData[index];
    root.x0 = height / 2;
    root.y0 = 0;
    update(root);
}


console.log("nibaba");
// ************** Generate the tree diagram  *****************
var margin = {top: 20, right: 120, bottom: 20, left: 120},
    width = 960 - margin.right - margin.left,
    height = 500 - margin.top - margin.bottom;

var i = 0,
    duration = 750,
    root;

var tree = d3.layout.tree()
    .size([height, width]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var svg = d3.select("#chart-area").append("svg")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

root = treeData[0];
root.x0 = height / 2;
root.y0 = 0;

//update(root);

d3.select(self.frameElement).style("height", "500px");


function update(source) {

    // Compute the new tree layout.
    var nodes = tree.nodes(root).reverse(),
        links = tree.links(nodes);

    // Normalize for fixed-depth.
    nodes.forEach(function(d) { d.y = d.depth * 180; });

    // Update the nodes…
    var node = svg.selectAll("g.node")
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
        .on("click", click);

    nodeEnter.append("circle")
        .attr("r", 1e-6)
        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

    nodeEnter.append("text")
        .attr("x", function(d) { return d.children || d._children ? -13 : 13; })
        .attr("dy", ".35em")
        .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
        .text(function(d) { return d.name; })
        .style("fill-opacity", 1e-6);

    // Transition nodes to their new position.
    var nodeUpdate = node.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

    nodeUpdate.select("circle")
        .attr("r", 10)
        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

    nodeUpdate.select("text")
        .style("fill-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
        .remove();

    nodeExit.select("circle")
        .attr("r", 1e-6);

    nodeExit.select("text")
        .style("fill-opacity", 1e-6);

    // Update the links…
    var link = svg.selectAll("path.link")
        .data(links, function(d) { return d.target.id; });

    // Enter any new links at the parent's previous position.
    link.enter().insert("path", "g")
        .attr("class", "link")
        .attr("d", function(d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
        });

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function(d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
        })
        .remove();

    // Stash the old positions for transition.
    nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

// Toggle children on click.
function click(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}



function make_histogram() {
    const color = "steelblue";

    // Generate a 1000 data points using normal distribution with mean=20, deviation=5
    var values = d3.range(1000).map(d3.random.normal(20, 5));

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 20, right: 30, bottom: 30, left: 30},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var max = d3.max(values);
    var min = d3.min(values);
    var x = d3.scale.linear()
        .domain([min, max])
        .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var data = d3.layout.histogram()
        .bins(x.ticks(20))
    (values);

    var yMax = d3.max(data, function(d){return d.length});
    var yMin = d3.min(data, function(d){return d.length});
    var colorScale = d3.scale.linear()
        .domain([yMin, yMax])
        .range([d3.rgb(color).brighter(), d3.rgb(color).darker()]);

    var y = d3.scale.linear()
        .domain([0, yMax])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var svg1 = d3.select("#chart-histogram").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    // .attr("width", "100%")
    // .attr("height", "100%")
        .attr("viewBox", "0 0 " + width + " " + height)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var bar = svg1.selectAll(".bar")
        .data(data)
        .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", (x(data[0].dx) - x(0)) - 1)
        .attr("height", function(d) { return height - y(d.y); })
        .attr("fill", function(d) { return colorScale(d.y) });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("x", (x(data[0].dx) - x(0)) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) { return formatCount(d.y); });

    svg1.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    /*
     * Adding refresh method to reload new data
     */
    function refresh(values){
        // var values = d3.range(1000).map(d3.random.normal(20, 5));
        var data = d3.layout.histogram()
            .bins(x.ticks(20))
        (values);

        // Reset y domain using new data
        var yMax = d3.max(data, function(d){return d.length});
        var yMin = d3.min(data, function(d){return d.length});
        y.domain([0, yMax]);
        var colorScale = d3.scale.linear()
            .domain([yMin, yMax])
            .range([d3.rgb(color).brighter(), d3.rgb(color).darker()]);

        var bar = svg1.selectAll(".bar").data(data);

        // Remove object with data
        bar.exit().remove();

        bar.transition()
            .duration(1000)
            .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

        bar.select("rect")
            .transition()
            .duration(1000)
            .attr("height", function(d) { return height - y(d.y); })
            .attr("fill", function(d) { return colorScale(d.y) });

        bar.select("text")
            .transition()
            .duration(1000)
            .text(function(d) { return formatCount(d.y); });

    }

    // Calling refresh repeatedly.
    // setInterval(function() {
    //   var values = d3.range(1000).map(d3.random.normal(20, 5));
    //   refresh(values);
    // }, 2000);
}
