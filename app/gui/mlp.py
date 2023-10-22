import json
import os
import tkinter as tk
from pickle import dump as pickle_dump
from pickle import load as pickle_load
# Seed
from random import seed
from tkinter import filedialog, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.random import seed as np_seed  # type: ignore
from pandastable import Table
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tensorflow import random
# Keras
from tensorflow.keras.backend import clear_session
from tensorflow.keras.initializers import GlorotUniform
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import SGD, Adam, RMSprop
from scikeras.wrappers import KerasRegressor

from .helpers import loss, popupmsg, skloss

seed(0)
np_seed(0)
random.set_seed(0)



class MultiLayerPerceptron:

    def __init__(self):
        self.root = ttk.Frame()
        # Get Train Set
        get_train_set_frame = ttk.Labelframe(self.root, text="Get Train Set")
        get_train_set_frame.grid(column=0, row=0)

        file_path = tk.StringVar(value="")
        ttk.Label(get_train_set_frame, text="Train File Path").grid(column=0,
                                                                    row=0)
        ttk.Entry(get_train_set_frame, textvariable=file_path).grid(column=1,
                                                                    row=0)
        ttk.Button(get_train_set_frame,
                   text="Read Data",
                   command=lambda: self.read_input_data(file_path)).grid(
                       column=2, row=0)

        self.input_list = tk.Listbox(get_train_set_frame)
        self.input_list.grid(column=0, row=1)
        self.input_list.bind("<Double-Button-1>", self.add_predictor)
        self.input_list.bind("<Double-Button-3>", self.add_target)

        self.predictor_list = tk.Listbox(get_train_set_frame)
        self.predictor_list.grid(column=1, row=1)
        self.predictor_list.bind("<Double-Button-1>", self.eject_predictor)

        self.target_list = tk.Listbox(get_train_set_frame)
        self.target_list.grid(column=2, row=1)
        self.target_list.bind("<Double-Button-1>", self.eject_target)

        ttk.Button(get_train_set_frame,
                   text="Add Predictor",
                   command=self.add_predictor).grid(column=1, row=2)
        ttk.Button(get_train_set_frame,
                   text="Eject Predictor",
                   command=self.eject_predictor).grid(column=1, row=3)

        ttk.Button(get_train_set_frame,
                   text="Add Target",
                   command=self.add_target).grid(column=2, row=2)
        ttk.Button(get_train_set_frame,
                   text="Eject Target",
                   command=self.eject_target).grid(column=2, row=3)

        # Model testing and validation
        model_validation_frame = ttk.Labelframe(
            self.root, text="Model testing and validation")
        model_validation_frame.grid(column=0, row=1)

        self.do_forecast_option = tk.IntVar(value=0)
        tk.Checkbutton(model_validation_frame,
                       text="Do Forecast",
                       offvalue=0,
                       onvalue=1,
                       variable=self.do_forecast_option,
                       command=self.open_other_entries).grid(column=0,
                                                             row=0,
                                                             columnspan=2)

        self.validation_option = tk.IntVar(value=0)
        self.random_percent_var = tk.IntVar(value=70)
        self.cross_val_var = tk.IntVar(value=5)
        tk.Radiobutton(model_validation_frame,
                       text="No validation, use all data rows",
                       value=0,
                       variable=self.validation_option,
                       command=self.open_other_entries).grid(column=0,
                                                             row=1,
                                                             columnspan=2,
                                                             sticky=tk.W)
        tk.Radiobutton(model_validation_frame,
                       text="Random percent",
                       value=1,
                       variable=self.validation_option,
                       command=self.open_other_entries).grid(column=0,
                                                             row=2,
                                                             sticky=tk.W)
        self.cv_entry_1 = tk.Radiobutton(model_validation_frame,
                                         text="K-fold cross-validation",
                                         value=2,
                                         variable=self.validation_option,
                                         command=self.open_other_entries,
                                         state=tk.DISABLED)
        self.cv_entry_1.grid(column=0, row=3, sticky=tk.W)
        self.cv_entry_2 = tk.Radiobutton(model_validation_frame,
                                         text="Leave one out cross-validation",
                                         value=3,
                                         variable=self.validation_option,
                                         command=self.open_other_entries,
                                         state=tk.DISABLED)
        self.cv_entry_2.grid(column=0, row=4, columnspan=2, sticky=tk.W)
        self.random_percent_entry = ttk.Entry(
            model_validation_frame,
            textvariable=self.random_percent_var,
            width=8,
            state=tk.DISABLED)
        self.random_percent_entry.grid(column=1, row=2)
        self.cv_value_entry = ttk.Entry(model_validation_frame,
                                        textvariable=self.cross_val_var,
                                        width=8,
                                        state=tk.DISABLED)
        self.cv_value_entry.grid(column=1, row=3)

        # Create Model
        create_model_frame = ttk.Labelframe(self.root, text="Create Model")
        create_model_frame.grid(column=1, row=0)

        self.do_optimization = False

        # Model Without Optimization
        model_without_optimization_frame = ttk.Labelframe(
            create_model_frame, text="Model Without Optimization")
        model_without_optimization_frame.grid(column=0, row=0)

        ttk.Label(model_without_optimization_frame,
                  text="Number of Hidden Layer").grid(column=0, row=0)

        layer_count = 20

        no_optimization_names = [
            "Neurons in First Layer", "Neurons in Second Layer",
            "Neurons in Third Layer", "Neurons in Fourth Layer",
            "Neurons in Fifth Layer"
        ]
        self.neuron_numbers_var = [
            tk.IntVar(value="") for _ in range(layer_count)
        ]  # type: ignore
        self.activation_var = [
            tk.StringVar(value="relu") for _ in range(layer_count)
        ]
        self.no_optimization_choice_var = tk.IntVar(value=0)

        self.no_optimization = [[
            tk.Radiobutton(model_without_optimization_frame,
                           text=str(i + 1),
                           value=i + 1,
                           variable=self.no_optimization_choice_var,
                           command=lambda: self.open_layers(True)).grid(
                               column=i + 1, row=0),
            ttk.Label(model_without_optimization_frame,
                      text=no_optimization_names[i]).grid(column=0, row=i + 1),
            ttk.Entry(model_without_optimization_frame,
                      textvariable=self.neuron_numbers_var[i],
                      state=tk.DISABLED),
            ttk.Label(model_without_optimization_frame,
                      text="Activation Function").grid(column=3,
                                                       row=i + 1,
                                                       columnspan=2),
            ttk.OptionMenu(model_without_optimization_frame,
                           self.activation_var[i], "relu", "relu", "tanh",
                           "sigmoid", "linear").grid(column=5, row=i + 1)
        ] for i in range(5)]

        self.output_activation = tk.StringVar(value="relu")
        ttk.Label(model_without_optimization_frame,
                  text="Output Activation").grid(column=1, row=7),
        ttk.OptionMenu(model_without_optimization_frame,
                       self.output_activation, "relu", "relu", "tanh",
                       "sigmoid", "linear").grid(column=2, row=7)

        top_level = tk.Toplevel(self.root)
        top_level.protocol("WM_DELETE_WINDOW", top_level.withdraw)
        top = ttk.Frame(top_level)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        for i in range(5, 20):
            self.no_optimization.append([
                tk.Radiobutton(top,
                               text=str(i + 1),
                               value=i + 1,
                               variable=self.no_optimization_choice_var,
                               command=lambda: self.open_layers(True)).grid(
                                   column=i + 1, row=0),
                ttk.Label(top,
                          text=f"Neurons in {i+1}. Layer:").grid(column=0,
                                                                 row=i + 1 - 5,
                                                                 columnspan=4),
                ttk.Entry(top,
                          textvariable=self.neuron_numbers_var[i],
                          state=tk.DISABLED),
                ttk.Label(top, text="Activation Function").grid(column=9,
                                                                row=i + 1 - 5,
                                                                columnspan=4),
                ttk.OptionMenu(top, self.activation_var[i], "relu", "relu",
                               "tanh", "sigmoid", "linear").grid(column=13,
                                                                 row=i + 1 - 5,
                                                                 columnspan=3)
            ])

        for i, j in enumerate(self.no_optimization):
            if i > 4:
                j[2].grid(column=4, row=i + 1 - 5, columnspan=5)
            else:
                j[2].grid(column=1, row=i + 1, columnspan=2)

        top_level.withdraw()

        ttk.Button(model_without_optimization_frame,
                   text="More Layers",
                   command=top_level.deiconify).grid(column=3, row=7)
        ttk.Button(top, text="Done", command=top_level.withdraw).grid(column=0,
                                                                      row=16)

        # Model With Optimization
        model_with_optimization_frame = ttk.Labelframe(
            create_model_frame, text="Model With Optimization")
        model_with_optimization_frame.grid(column=0, row=1)

        optimization_names = [
            "One Hidden Layer", "Two Hidden Layer", "Three Hidden Layer"
        ]
        self.optimization_choice_var = tk.IntVar(value=0)
        self.min_max_neuron_numbers = [
            [tk.IntVar(value=""), tk.IntVar(value="")] for _ in range(3)
        ]  # type: ignore

        self.optimization = [[
            tk.Radiobutton(model_with_optimization_frame,
                           text=optimization_names[i],
                           value=i + 1,
                           variable=self.optimization_choice_var,
                           command=lambda: self.open_layers(False)).grid(
                               column=i * 2 + 1, row=0),
            ttk.Label(model_with_optimization_frame,
                      text=f"N{i+1}_Min").grid(column=i * 2, row=1),
            ttk.Label(model_with_optimization_frame,
                      text=f"N{i+1}_Max").grid(column=i * 2, row=2),
            ttk.Entry(model_with_optimization_frame,
                      textvariable=self.min_max_neuron_numbers[i][0],
                      state=tk.DISABLED),
            ttk.Entry(model_with_optimization_frame,
                      textvariable=self.min_max_neuron_numbers[i][1],
                      state=tk.DISABLED),
        ] for i in range(3)]

        for i, j in enumerate(self.optimization):
            j[3].grid(column=i * 2 + 1, row=1)
            j[4].grid(column=i * 2 + 1, row=2)

        # Hyperparameters
        hyperparameter_frame = ttk.Labelframe(self.root,
                                              text="Hyperparameters")
        hyperparameter_frame.grid(column=1, row=1)

        self.hyperparameters = [
            tk.IntVar(),
            tk.IntVar(),
            tk.StringVar(),
            tk.StringVar(),
            tk.DoubleVar(value=0.001),
            tk.DoubleVar(value=0.0)
        ]

        ttk.Label(hyperparameter_frame, text="Epoch").grid(column=0, row=0)
        ttk.Entry(hyperparameter_frame,
                  textvariable=self.hyperparameters[0]).grid(column=1, row=0)

        ttk.Label(hyperparameter_frame, text="Batch Size").grid(column=2,
                                                                row=0)
        ttk.Entry(hyperparameter_frame,
                  textvariable=self.hyperparameters[1]).grid(column=3, row=0)

        ttk.Label(hyperparameter_frame, text="Optimizer").grid(column=0, row=1)
        ttk.OptionMenu(hyperparameter_frame, self.hyperparameters[2], "Adam",
                       "Adam", "SGD", "RMSprop").grid(column=1, row=1)

        ttk.Label(hyperparameter_frame, text="Loss_Function").grid(column=2,
                                                                   row=1)
        ttk.OptionMenu(hyperparameter_frame, self.hyperparameters[3],
                       "mean_squared_error", "mean_squared_error",
                       "mean_absolute_error",
                       "mean_absolute_percentage_error").grid(column=3, row=1)

        ttk.Label(hyperparameter_frame, text="Learning Rate").grid(column=0,
                                                                   row=2)
        ttk.Entry(hyperparameter_frame,
                  textvariable=self.hyperparameters[4]).grid(column=1, row=2)

        ttk.Label(hyperparameter_frame,
                  text="Momentum (Between 0-1)").grid(column=2, row=2)
        ttk.Entry(hyperparameter_frame,
                  textvariable=self.hyperparameters[5]).grid(column=3, row=2)

        ttk.Button(hyperparameter_frame,
                   text="Create Model",
                   command=self.create_model).grid(column=0, row=5)
        ttk.Button(hyperparameter_frame,
                   text="Save Model",
                   command=self.save_model).grid(column=3, row=5)

        # Customize Train Set
        customize_train_set_frame = ttk.LabelFrame(self.root,
                                                   text="Custome Train Set")
        customize_train_set_frame.grid(column=0, row=2)

        self.lookback_option = tk.IntVar(value=0)
        self.lookback_val_var = tk.IntVar(value="")  # type: ignore
        tk.Checkbutton(customize_train_set_frame,
                       text="Lookback",
                       offvalue=0,
                       onvalue=1,
                       variable=self.lookback_option,
                       command=self.open_other_entries).grid(column=0, row=0)
        self.lookback_entry = ttk.Entry(customize_train_set_frame,
                                        textvariable=self.lookback_val_var,
                                        width=8,
                                        state=tk.DISABLED)
        self.lookback_entry.grid(column=1, row=0)

        self.seasonal_lookback_option = tk.IntVar(value=0)
        self.seasonal_period_var = tk.IntVar(value="")  # type: ignore
        self.seasonal_val_var = tk.IntVar(value="")  # type: ignore
        tk.Checkbutton(customize_train_set_frame,
                       text="Periodic Lookback",
                       offvalue=0,
                       onvalue=1,
                       variable=self.seasonal_lookback_option,
                       command=self.open_other_entries).grid(column=0, row=1)
        self.seasonal_lookback_entry_1 = ttk.Entry(
            customize_train_set_frame,
            textvariable=self.seasonal_period_var,
            width=8,
            state=tk.DISABLED)
        self.seasonal_lookback_entry_1.grid(column=0, row=2)
        self.seasonal_lookback_entry_2 = ttk.Entry(
            customize_train_set_frame,
            textvariable=self.seasonal_val_var,
            width=8,
            state=tk.DISABLED)
        self.seasonal_lookback_entry_2.grid(column=1, row=2)

        self.scale_var = tk.StringVar(value="None")
        ttk.Label(customize_train_set_frame, text="Scale Type").grid(column=0,
                                                                     row=3)
        ttk.OptionMenu(customize_train_set_frame, self.scale_var, "None",
                       "None", "StandardScaler", "MinMaxScaler").grid(column=1,
                                                                      row=3)

        # Test Model
        test_model_frame = ttk.LabelFrame(self.root, text="Test Frame")
        test_model_frame.grid(column=1, row=2)

        # Test Model Main
        test_model_main_frame = ttk.LabelFrame(test_model_frame,
                                               text="Test Model")
        test_model_main_frame.grid(column=0, row=0)

        self.forecast_num = tk.IntVar(value="")  # type: ignore
        ttk.Label(test_model_main_frame, text="# of Forecast").grid(column=0,
                                                                    row=0)
        ttk.Entry(test_model_main_frame,
                  textvariable=self.forecast_num).grid(column=1, row=0)
        ttk.Button(test_model_main_frame,
                   text="Values",
                   command=self.show_predicts).grid(column=2, row=0)

        test_file_path = tk.StringVar()
        ttk.Label(test_model_main_frame, text="Test File Path").grid(column=0,
                                                                     row=1)
        ttk.Entry(test_model_main_frame,
                  textvariable=test_file_path).grid(column=1, row=1)
        ttk.Button(test_model_main_frame,
                   text="Get Test Set",
                   command=lambda: self.get_test_set(test_file_path)).grid(
                       column=2, row=1)

        ttk.Button(test_model_main_frame,
                   text="Test Model",
                   command=self.forecast).grid(column=2, row=3)
        ttk.Button(test_model_main_frame,
                   text="Actual vs Forecast Graph",
                   command=self.plot_graph).grid(column=0, row=4, columnspan=3)

        ttk.Button(test_model_main_frame,
                   text="Load Model",
                   command=self.load_model).grid(column=0, row=3)

        # Test Model Metrics
        test_model_metrics_frame = ttk.LabelFrame(test_model_frame,
                                                  text="Test Metrics")
        test_model_metrics_frame.grid(column=1, row=0)

        test_metrics = ["NMSE", "RMSE", "MAE", "MAPE", "SMAPE"]
        self.test_metrics_vars = [
            tk.Variable() for _ in range(len(test_metrics))
        ]
        for i, j in enumerate(test_metrics):
            ttk.Label(test_model_metrics_frame, text=j).grid(column=0, row=i)
            ttk.Entry(test_model_metrics_frame,
                      textvariable=self.test_metrics_vars[i]).grid(column=1,
                                                                   row=i)

    def read_input_data(self, file_path):
        path = filedialog.askopenfilename(
            filetypes=[("Csv Files",
                        "*.csv"), ("Xlsx Files",
                                   "*.xlsx"), ("Xlrd Files", ".xls")])
        if not path:
            return
        file_path.set(path)
        if path.endswith(".csv"):
            self.df = pd.read_csv(path)  # type: ignore
        else:
            try:
                self.df = pd.read_excel(path)
            except Exception:
                self.df = pd.read_excel(path, engine="openpyxl")
        self.df: pd.DataFrame
        self.fill_input_list()

    def fill_input_list(self):
        self.input_list.delete(0, tk.END)
        self.predictor_list.delete(0, tk.END)
        self.target_list.delete(0, tk.END)

        self.df: pd.DataFrame

        for i in self.df.columns.tolist():
            self.input_list.insert(tk.END, i)

    def get_test_set(self, file_path):
        path = filedialog.askopenfilename(
            filetypes=[("Csv Files",
                        "*.csv"), ("Xlsx Files",
                                   "*.xlsx"), ("Xlrd Files", ".xls")])
        if not path:
            return
        file_path.set(path)
        if path.endswith(".csv"):
            self.test_df = pd.read_csv(path)  # type: ignore
        else:
            try:
                self.test_df = pd.read_excel(path)
            except Exception:
                self.test_df = pd.read_excel(path, engine="openpyxl")

    def show_predicts(self):
        try:
            df = pd.DataFrame({"Test": self.y_test, "Predict": self.pred})
        except Exception:
            return
        top = tk.Toplevel(self.root)
        pt = Table(top, dataframe=df, editable=False)
        pt.show()

    def add_predictor(self, event=None):
        try:
            a = self.input_list.get(self.input_list.curselection())
            if a not in self.predictor_list.get(0, tk.END):
                self.predictor_list.insert(tk.END, a)
        except Exception:
            pass

    def eject_predictor(self, event=None):
        try:
            self.predictor_list.delete(self.predictor_list.curselection())
        except Exception:
            pass

    def add_target(self, event=None):
        try:
            a = self.input_list.get(self.input_list.curselection())
            if self.target_list.size() < 1:
                self.target_list.insert(tk.END, a)
        except Exception:
            pass

    def eject_target(self, event=None):
        try:
            self.target_list.delete(self.target_list.curselection())
        except Exception:
            pass

    def open_layers(self, var):
        for i in self.no_optimization:
            i[2]["state"] = tk.DISABLED
        for i in self.optimization:
            i[3]["state"] = tk.DISABLED
            i[4]["state"] = tk.DISABLED

        if var:
            for i in range(self.no_optimization_choice_var.get()):
                self.no_optimization[i][2]["state"] = tk.NORMAL
            self.optimization_choice_var.set(0)
            self.do_optimization = False

        if not var:
            for i in range(self.optimization_choice_var.get()):
                self.optimization[i][3]["state"] = tk.NORMAL
                self.optimization[i][4]["state"] = tk.NORMAL
            self.no_optimization_choice_var.set(0)
            self.do_optimization = True

    def open_other_entries(self):
        if not self.do_forecast_option.get():
            self.cv_entry_1["state"] = tk.NORMAL
            self.cv_entry_2["state"] = tk.NORMAL
        else:
            self.cv_entry_1["state"] = tk.DISABLED
            self.cv_entry_2["state"] = tk.DISABLED
        if self.validation_option.get() == 1:
            self.random_percent_entry["state"] = tk.NORMAL
        else:
            self.random_percent_entry["state"] = tk.DISABLED
        if self.validation_option.get() == 2:
            self.cv_value_entry["state"] = tk.NORMAL
        else:
            self.cv_value_entry["state"] = tk.DISABLED
        if self.lookback_option.get():
            self.lookback_entry["state"] = tk.NORMAL
        else:
            self.lookback_entry["state"] = tk.DISABLED
        if self.seasonal_lookback_option.get():
            self.seasonal_lookback_entry_1["state"] = tk.NORMAL
            self.seasonal_lookback_entry_2["state"] = tk.NORMAL
        else:
            self.seasonal_lookback_entry_1["state"] = tk.DISABLED
            self.seasonal_lookback_entry_2["state"] = tk.DISABLED

    def save_model(self):
        path = filedialog.asksaveasfilename()
        if not path:
            return
        try:
            params = {
                "predictor_names":
                self.predictor_names,
                "label_name":
                self.label_name,
                "is_round":
                self.is_round,
                "is_negative":
                self.is_negative,
                "do_forecast":
                self.do_forecast_option.get(),
                "validation_option":
                self.validation_option.get(),
                "random_percent":
                self.random_percent_var.get()
                if self.validation_option.get() == 1 else None,
                "k_fold_cv":
                self.cross_val_var.get()
                if self.validation_option.get() == 2 else None,
                "lookback_option":
                self.lookback_option.get(),
                "lookback_value":
                self.lookback_val_var.get()
                if self.lookback_option.get() else None,
                "seasonal_lookback_option":
                self.seasonal_lookback_option.get(),
                "seasonal_period":
                self.seasonal_period_var.get()
                if self.seasonal_lookback_option.get() else None,
                "seasonal_value":
                self.seasonal_val_var.get()
                if self.seasonal_lookback_option.get() else None,
                "sliding":
                self.sliding,
                "scale_type":
                self.scale_var.get(),
                "num_layers":
                self.no_optimization_choice_var.get(),
                "num_neurons": [
                    self.neuron_numbers_var[i].get()
                    for i in range(self.no_optimization_choice_var.get())
                ],
                "activations": [
                    self.activation_var[i].get()
                    for i in range(self.no_optimization_choice_var.get())
                ],
                "output_activation":
                self.output_activation.get(),
                "hyperparameters": [i.get() for i in self.hyperparameters],
            }
        except Exception:
            popupmsg("Model is not created")
            return

        os.mkdir(path)
        self.model: Sequential
        self.model.save(path + "/model.h5")
        if self.scale_var.get() != "None":
            with open(path + "/feature_scaler.pkl", "wb") as f:
                pickle_dump(self.feature_scaler, f)
            with open(path + "/label_scaler.pkl", "wb") as f:
                pickle_dump(self.label_scaler, f)
        if self.lookback_option.get() == 1:
            with open(path + "/last_values.npy", 'wb') as outfile:
                np.save(outfile, self.last)
        if self.seasonal_lookback_option.get() == 1:
            with open(path + "/seasonal_last_values.npy", 'wb') as outfile:
                np.save(outfile, self.seasonal_last)
        with open(path + "/model.json", 'w') as outfile:
            json.dump(params, outfile)

    def load_model(self):
        path = filedialog.askdirectory()
        if not path:
            return
        try:
            self.model = load_model(path + "/model.h5")  # type: ignore
        except Exception:
            popupmsg("There is no model file at the path")
        infile = open(path + "/model.json")
        params = json.load(infile)
        infile.close()

        self.predictor_names = params["predictor_names"]
        self.label_name = params["label_name"]
        try:
            self.is_round = params["is_round"]
        except Exception:
            self.is_round = True
        try:
            self.is_negative = params["is_negative"]
        except Exception:
            self.is_negative = False
        self.do_forecast_option.set(params["do_forecast"])
        self.validation_option.set(params["validation_option"])
        if params["validation_option"] == 1:
            self.random_percent_var.set(params["random_percent"])
        elif params["validation_option"] == 2:
            self.cross_val_var.set(params["k_fold_cv"])
        self.lookback_option.set(params["lookback_option"])
        self.sliding = -1
        if params["lookback_option"] == 1:
            self.lookback_val_var.set(params["lookback_value"])
            last_values = open(path + "/last_values.npy", 'rb')
            self.last = np.load(last_values)
            last_values.close()
            self.sliding = 0
        try:
            self.sliding = params["sliding"]
            self.seasonal_lookback_option.set(
                params["seasonal_lookback_option"])
            if params["seasonal_lookback_option"] == 1:
                self.seasonal_period_var.set(params["seasonal_period"])
                self.seasonal_val_var.set(params["seasonal_value"])
                seasonal_last_values = open(path + "/seasonal_last_values.npy",
                                            'rb')
                self.seasonal_last = np.load(seasonal_last_values)
                seasonal_last_values.close()
        except Exception:
            pass
        self.scale_var.set(params["scale_type"])
        if params["scale_type"] != "None":
            try:
                with open(path + "/feature_scaler.pkl", "rb") as f:
                    self.feature_scaler = pickle_load(f)
                with open(path + "/label_scaler.pkl", "rb") as f:
                    self.label_scaler = pickle_load(f)
            except Exception:
                pass
        self.no_optimization_choice_var.set(params["num_layers"])
        [
            self.neuron_numbers_var[i].set(j)
            for i, j in enumerate(params["num_neurons"])
        ]
        [
            self.activation_var[i].set(j)
            for i, j in enumerate(params["activations"])
        ]
        try:
            self.output_activation.set(params["output_activation"])
        except Exception:
            self.output_activation.set("relu")
        [
            self.hyperparameters[i].set(j)
            for i, j in enumerate(params["hyperparameters"])
        ]

        self.open_layers(True)
        self.open_other_entries()
        names = "\n".join(self.predictor_names)
        msg = f"Predictor names are {names}\nLabel name is {self.label_name}"
        popupmsg(msg)
        # self.getData()

    def check_errors(self):
        try:
            msg = "Read a data frist"
            self.df.head(1)

            msg = "Select predictors"
            if not self.predictor_list.get(0):
                raise Exception

            msg = "Select a target"
            if not self.target_list.get(0):
                raise Exception

            msg = "Target and predictor have same variable"
            if self.target_list.get(0) in self.predictor_list.get(0, tk.END):
                raise Exception

            msg = "Enter a valid percent value"
            if self.random_percent_var.get() <= 0:
                raise Exception

            msg = "Enter a valid K-fold value (Above 2)"
            if self.validation_option.get(
            ) == 2 and self.cross_val_var.get() <= 1:
                raise Exception

            msg = "Enter a valid lookback value"
            if self.lookback_option.get():
                self.lookback_val_var.get()

            msg = "Enter valid periodic lookback values"
            if self.seasonal_lookback_option.get():
                self.seasonal_val_var.get()
                self.seasonal_period_var.get()

            msg = "Select a valid layer number"
            if not self.no_optimization_choice_var.get():
                raise Exception

            msg = "Enter a valid neuron number"
            neuron_empty = False
            for i in range(self.no_optimization_choice_var.get()):
                try:
                    self.neuron_numbers_var[i].get()
                except Exception:
                    neuron_empty = True
            if neuron_empty:
                raise Exception

            msg = "Enter a valid Epoch size"
            if self.hyperparameters[0].get() <= 0:
                raise Exception

            msg = "Enter a valid Batch size"
            if self.hyperparameters[1].get() <= 0:
                raise Exception

            msg = "Enter a valid Learning Rate"
            if self.hyperparameters[-2].get() <= 0:
                raise Exception

            msg = "Enter a valid Momentum value"
            if self.hyperparameters[2].get() != "Adam" and float(
                    self.hyperparameters[-1].get()) < 0:
                raise Exception

            return False
        except Exception:
            popupmsg(msg)  # type: ignore
            return True

    def get_lookback(self,
                     X,
                     y,
                     lookback=0,
                     seasons=0,
                     seasonal_lookback=0,
                     sliding=-1):
        if sliding == 0:
            for i in range(1, lookback + 1):
                X[f"t-{i}"] = y.shift(i)
        elif sliding == 1:
            for i in range(1, seasons + 1):
                X[f"t-{i*seasonal_lookback}"] = y.shift(i * seasonal_lookback)
        elif sliding == 2:
            for i in range(1, lookback + 1):
                X[f"t-{i}"] = y.shift(i)
            for i in range(1, seasons + 1):
                X[f"t-{i*seasonal_lookback}"] = y.shift(i * seasonal_lookback)

        X.dropna(inplace=True)
        a = X.to_numpy()
        b = y.iloc[-len(a):].to_numpy().reshape(-1)

        if sliding == 0:
            self.last = b[-lookback:]
        elif sliding == 1:
            self.seasonal_last = b[-seasonal_lookback * seasons:]
        elif sliding == 2:
            self.last = b[-(lookback + seasonal_lookback):-seasonal_lookback]
            self.seasonal_last = b[-seasonal_lookback * seasons:]

        return a, b

    def get_data(self):
        self.is_round = False
        self.is_negative = False
        lookback_option = self.lookback_option.get()
        seasonal_lookback_option = self.seasonal_lookback_option.get()
        sliding = lookback_option + 2 * seasonal_lookback_option - 1
        self.sliding = sliding
        scale_choice = self.scale_var.get()

        self.predictor_names = list(self.predictor_list.get(0, tk.END))
        self.label_name = self.target_list.get(0)

        self.df: pd.DataFrame
        X = self.df[self.predictor_names].copy()
        y = self.df[self.label_name].copy()

        if y.dtype == int or y.dtype == np.intc or y.dtype == np.int64:
            self.is_round = True
        if any(y < 0):
            self.is_negative = True

        if scale_choice == "StandardScaler":
            self.feature_scaler = StandardScaler()
            self.label_scaler = StandardScaler()

            X.iloc[:] = self.feature_scaler.fit_transform(X)
            y.iloc[:] = self.label_scaler.fit_transform(y.values.reshape(
                -1, 1)).reshape(-1)

        elif scale_choice == "MinMaxScaler":
            self.feature_scaler = MinMaxScaler()
            self.label_scaler = MinMaxScaler()

            X.iloc[:] = self.feature_scaler.fit_transform(X)
            y.iloc[:] = self.label_scaler.fit_transform(y.values.reshape(
                -1, 1)).reshape(-1)

        try:
            lookback = self.lookback_val_var.get()
        except Exception:
            lookback = 0
        try:
            seasonal_period = self.seasonal_period_var.get()
            seasonal_lookback = self.seasonal_val_var.get()
        except Exception:
            seasonal_period = 0
            seasonal_lookback = 0

        X, y = self.get_lookback(X, y, lookback, seasonal_period,
                                 seasonal_lookback, sliding)

        return X, y

    def create_model(self):
        clear_session()
        if self.check_errors():
            return
        X, y = self.get_data()
        X: np.ndarray
        y: np.ndarray

        layers = self.no_optimization_choice_var.get()

        learning_rate = self.hyperparameters[4].get()
        if self.hyperparameters[2] != "Adam":
            momentum = self.hyperparameters[5].get()

        optimizers = {
            "Adam": Adam(learning_rate=learning_rate),
            "SGD": SGD(learning_rate=learning_rate, momentum=momentum),
            "RMSprop": RMSprop(learning_rate=learning_rate, momentum=momentum)
        }

        def base_model():
            model = Sequential()

            for i in range(layers):
                neuron_number = self.neuron_numbers_var[i].get()
                activation = self.activation_var[i].get()
                if i == 0:
                    model.add(
                        Dense(neuron_number,
                              activation=activation,
                              input_dim=X.shape[1],
                              kernel_initializer=GlorotUniform(seed=0)))
                    model.add(Dropout(0.2))
                else:
                    model.add(
                        Dense(neuron_number,
                              activation=activation,
                              kernel_initializer=GlorotUniform(seed=0)))
                    model.add(Dropout(0.2))

            model.add(
                Dense(1,
                      activation=self.output_activation.get(),
                      kernel_initializer=GlorotUniform(seed=0)))
            model.compile(optimizer=optimizers[self.hyperparameters[2].get()],
                          loss=self.hyperparameters[3].get())
            return model

        do_forecast = self.do_forecast_option.get()
        val_option = self.validation_option.get()

        if val_option == 0:
            model = base_model()
            model.fit(X,
                      y,
                      epochs=self.hyperparameters[0].get(),
                      batch_size=self.hyperparameters[1].get())
            if do_forecast == 0:
                pred = model.predict(X).reshape(-1)
                if self.scale_var.get() != "None":
                    pred = self.label_scaler.inverse_transform(
                        pred.reshape(-1, 1)).reshape(-1)  # type: ignore
                    y = self.label_scaler.inverse_transform(y.reshape(
                        -1, 1)).reshape(-1)  # type: ignore
                losses = loss(y, pred)
                self.y_test = y
                self.pred = pred
                for i, j in enumerate(losses):
                    self.test_metrics_vars[i].set(j)
            self.model = model

        elif val_option == 1:
            model = base_model()
            if do_forecast == 0:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, train_size=self.random_percent_var.get() / 100)
                model.fit(X_train,
                          y_train,
                          epochs=self.hyperparameters[0].get(),
                          batch_size=self.hyperparameters[1].get())
                pred = model.predict(X_test).reshape(-1)
                if self.scale_var.get() != "None":
                    pred = self.label_scaler.inverse_transform(
                        pred.reshape(-1, 1)).reshape(-1)  # type: ignore
                    y_test = self.label_scaler.inverse_transform(
                        y_test.reshape(-1, 1)).reshape(-1)  # type: ignore
                losses = loss(y_test, pred)
                self.y_test = y_test
                self.pred = pred
                for i, j in enumerate(losses):
                    self.test_metrics_vars[i].set(j)
            else:
                size = int((self.random_percent_var.get() / 100) * len(X))
                X = X[-size:]
                y = y[-size:]
                model.fit(X,
                          y,
                          epochs=self.hyperparameters[0].get(),
                          batch_size=self.hyperparameters[1].get())
            self.model = model

        elif val_option == 2:
            model = KerasRegressor(build_fn=base_model,
                                   epochs=self.hyperparameters[0].get(),
                                   batch_size=self.hyperparameters[1].get())
            if do_forecast == 0:
                cvs = cross_validate(model,
                                     X,
                                     y,
                                     cv=self.cross_val_var.get(),
                                     scoring=skloss)
                for i, j in enumerate(list(cvs.values())[2:]):
                    self.test_metrics_vars[i].set(j.mean())

        elif val_option == 3:
            model = KerasRegressor(build_fn=base_model,
                                   epochs=self.hyperparameters[0].get(),
                                   batch_size=self.hyperparameters[1].get())
            if do_forecast == 0:
                cvs = cross_validate(model,
                                     X,
                                     y,
                                     cv=X.shape[0] - 1,
                                     scoring=skloss)
                for i, j in enumerate(list(cvs.values())[2:]):
                    self.test_metrics_vars[i].set(j.mean())

    def forecast_lookback(self,
                          num,
                          lookback=0,
                          seasons=0,
                          seasonal_lookback=0,
                          sliding=-1):
        self.test_df: pd.DataFrame
        self.model: Sequential
        pred = []
        if sliding == 0:
            last = self.last
            for i in range(num):
                X_test = self.test_df[self.predictor_names].iloc[i]
                if self.scale_var.get() != "None":
                    X_test.iloc[:] = self.feature_scaler.transform(
                        X_test.values.reshape(1,
                                              -1)).reshape(-1)  # type: ignore
                for j in range(1, lookback + 1):
                    X_test[f"t-{j}"] = last[-j]  # type: ignore
                to_pred = X_test.to_numpy().reshape(1, -1)  # type: ignore
                out = self.model.predict(to_pred)
                last = np.append(last, out)[-lookback:]
                pred.append(out)

        elif sliding == 1:
            seasonal_last = self.seasonal_last
            for i in range(num):
                X_test = self.test_df[self.predictor_names].iloc[i]
                if self.scale_var.get() != "None":
                    X_test.iloc[:] = self.feature_scaler.transform(
                        X_test.values.reshape(1,
                                              -1)).reshape(-1)  # type: ignore
                for j in range(1, seasons + 1):
                    X_test[f"t-{j*seasonal_last}"] = seasonal_last[
                        -j * seasonal_lookback]  # type: ignore
                to_pred = X_test.to_numpy().reshape(1, -1)  # type: ignore
                out = self.model.predict(to_pred)
                seasonal_last = np.append(seasonal_last, out)[1:]
                pred.append(out)

        elif sliding == 2:
            last = self.last
            seasonal_last = self.seasonal_last
            for i in range(num):
                X_test = self.test_df[self.predictor_names].iloc[i]
                if self.scale_var.get() != "None":
                    X_test.iloc[:] = self.feature_scaler.transform(
                        X_test.values.reshape(1,
                                              -1)).reshape(-1)  # type: ignore
                for j in range(1, lookback + 1):
                    X_test[f"t-{j}"] = last[-j]  # type: ignore
                for j in range(1, seasons + 1):
                    X_test[f"t-{j*seasonal_lookback}"] = seasonal_last[
                        -j * seasonal_lookback]  # type: ignore
                to_pred = X_test.to_numpy().reshape(1, -1)  # type: ignore
                out = self.model.predict(to_pred)
                last = np.append(last, out)[-lookback:]
                seasonal_last = np.append(seasonal_last, out)[1:]
                pred.append(out)

        return np.array(pred).reshape(-1)

    def forecast(self):
        try:
            num = self.forecast_num.get()
        except Exception:
            popupmsg("Enter a valid Forecast value")
            return
        lookback_option = self.lookback_option.get()
        seasonal_lookback_option = self.seasonal_lookback_option.get()
        try:
            X_test = self.test_df[
                self.predictor_names][:num].to_numpy()  # type: ignore
            y_test = self.test_df[self.label_name][:num].to_numpy().reshape(
                -1)  # type: ignore
            self.y_test = y_test
        except Exception:
            popupmsg("Enter a test data")
            return

        if lookback_option == 0 and seasonal_lookback_option == 0:
            if self.scale_var.get() != "None":
                X_test = self.feature_scaler.transform(X_test)
            self.pred = self.model.predict(X_test).reshape(-1)
        else:
            sliding = self.sliding
            try:
                lookback = self.lookback_val_var.get()
            except Exception:
                lookback = 0
            try:
                seasonal_lookback = self.seasonal_val_var.get()
                seasons = self.seasonal_period_var.get()
            except Exception:
                seasonal_lookback = 0
                seasons = 0

            self.pred = self.forecast_lookback(num, lookback, seasons,
                                               seasonal_lookback, sliding)

        if self.scale_var.get() != "None":
            self.pred = self.label_scaler.inverse_transform(
                self.pred.reshape(-1, 1)).reshape(-1)  # type: ignore

        if not self.is_negative:
            self.pred = self.pred.clip(0, None)
        if self.is_round:
            self.pred = np.round(self.pred).astype(int)

        losses = loss(y_test, self.pred)
        for i in range(len(self.test_metrics_vars)):
            self.test_metrics_vars[i].set(losses[i])

    def plot_graph(self):
        try:
            y_test = self.y_test
        except Exception:
            return
        pred = self.pred
        plt.plot(y_test)
        plt.plot(pred)
        plt.legend(["test", "pred"], loc="upper left")
        plt.show()
