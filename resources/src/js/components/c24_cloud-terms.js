if (document.getElementById("cloudWrap")) {
  /*-------------------*\
    Using prefix ag-
  /*-------------------*/
  am4core.options.autoSetClassName = true;
  am4core.options.classNamePrefix = "ag-";

  /*-------------------------------*\
    Config of Theme
      - Create instance of amChart
      - Create graphs for the theme
  /*-------------------------------*/
  const chart = am4core.create(
    "cloudWrap",
    am4plugins_forceDirected.ForceDirectedTree
  );
  const networkSeries = chart.series.push(
    new am4plugins_forceDirected.ForceDirectedSeries()
  );

  /*------------------------------*\
    Data for Graph
      - DOM data
      - Push data for the Graph
  /*------------------------------*/
  let jsonData = [];

  const jsonHtml = JSON.parse(
    JSON.parse(document.getElementById("data-cloud").text)
  );

  for (const key in jsonHtml) {
    if (jsonHtml.hasOwnProperty(key)) {
      let newsJsonData = {
        name: key,
        value: jsonHtml[key]
      };
      jsonData.push(newsJsonData);
    }
  }

  /*-----------------------------*\
    Config of Data for the plugin
  /*-----------------------------*/
  networkSeries.data = jsonData;
  networkSeries.dataFields.name = "name";
  networkSeries.dataFields.id = "name";
  networkSeries.dataFields.value = "value";
  networkSeries.fontSize = 10;

  /*----------------------*\
    Tooltip help
  /*----------------------*/
  networkSeries.tooltip.getFillFromObject = false;
  networkSeries.tooltip.background.filters.clear(); // Delete shadow
  networkSeries.tooltip.background.strokeWidth = 1; // Width for stroke tooltip
  networkSeries.tooltip.background.stroke = am4core.color("#d3d3d3"); // Color stroke tooltip
  networkSeries.tooltip.background.fill = am4core.color("#FFF"); // Color bg tooltip
  networkSeries.nodes.template.tooltipHTML = `<div class="ag-c-cloud__tooltip">
  <h5 style="margin:0;"> {name} </h5> <small style="margin:0;"> {value} </small></div>`;

  /*----------------------*\
    Styles for the circle
  /*----------------------*/
  networkSeries.nodes.template.outerCircle.scale = 1;
  networkSeries.nodes.template.fillOpacity = 1;
  networkSeries.minRadius = am4core.percent(2);
  networkSeries.manyBodyStrength = -12;

  /*--------------------------*\
    Styles for text of circle
  /*--------------------------*/
  networkSeries.nodes.template.label.hideOversized = false;
  networkSeries.nodes.template.label.truncate = false;
  networkSeries.nodes.template.label.html = `<div class="ag-c-cloud__box">
  <strong class='ag-c-cloud__lead'>{name}</strong>
  <span style='font-size:10px' class='ag-c-cloud__lead ag-c-cloud__lead_top'>({value})</span>
  </div>`;

  setTimeout(() => {
    const cloudItem = Array.from(
      document.querySelectorAll("g[role='menuitem']")
    );
    const modalItem = Array.from(
      document.getElementsByClassName("js-modalCloud")
    );

    /*------------------------------*\
      Add attr data_cloud in cloud
    /*------------------------------*/
    let keyDate = [];
    for (const key in jsonHtml) {
      let newDate = {
        keys: key
      };
      keyDate.push(newDate);
    }

    for (let i = 0; i < cloudItem.length; i++) {
      let cloudList = cloudItem[i];
      const strCloud = keyDate[i];
      if (strCloud.keys.length > 4) {
        cloudList.setAttribute("data-cloud", "cloud_" + i);
      } else {
        const attDataCloud = strCloud.keys.replace(" ", "-").toLowerCase();
        cloudList.setAttribute("data-cloud", "cloud_" + attDataCloud);
      }
    }

    /*------------------*\
      Event Show Modal
    /*------------------*/
    function showModalCloud(eventListener) {
      cloudItem.map(cloud => {
        cloud.addEventListener(eventListener, () => {
          for (let i = 0; i < modalItem.length; i++) {
            const listElementsCloud = modalItem[i];
            if (
              cloud.getAttribute("data-cloud") ==
              listElementsCloud.getAttribute("data-cloud")
            ) {
              listElementsCloud.style.display = "block";
              if (listElementsCloud.classList.contains("ag-js-card-grid")) {
                listElementsCloud.style.display = "flex";
              }
              document
                .querySelector(".js-modalClouds")
                .classList.add("ag-is-modal_visible");
              window.document.body.classList.add("ag-is-overflow");
            }
          }
        });
      });
    }

    /*-----------------*\
      Event Hide Modal
    /*-----------------*/
    function hideModalCloud() {
      const btnCloseModalCloud = document.querySelector(
        ".ag-js-modalCloudClose"
      );
      const parentModal = document.querySelector(".js-modalClouds");
      btnCloseModalCloud.addEventListener("click", () => {
        if (parentModal.classList.contains("ag-is-modal_visible")) {
          document
            .querySelector(".js-modalClouds")
            .classList.remove("ag-is-modal_visible");
          window.document.body.classList.remove("ag-is-overflow");
          for (let i = 0; i < modalItem.length; i++) {
            const listElementsCloud = modalItem[i];
            listElementsCloud.style.display = "none";
          }
        }
      });
    }

    /*-----------------*\
      Hover in Cloud
    /*-----------------*/
    function hoverCloud() {
      cloudItem.map(cloud => {
        cloud.addEventListener("mouseover", () => {
          cloud.classList.add("ag-js-cloud-hover");
        });
        cloud.addEventListener("mouseout", () => {
          cloud.classList.remove("ag-js-cloud-hover");
        });
      });
    }

    showModalCloud("touchend");
    showModalCloud("click");
    hideModalCloud();
    hoverCloud();
  }, 100);
}
